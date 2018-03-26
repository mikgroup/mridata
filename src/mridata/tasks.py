from celery.decorators import task
from celery.utils.log import get_task_logger

import os
import shutil
import traceback
import ismrmrd
import subprocess
import numpy as np
import boto3
from .recon import ifftc, rss, zpad, crop
from .models import Uploader, Data, TempData, PhilipsData, SiemensData, GeData, IsmrmrdData
from PIL import Image

from django.conf import settings
from django.shortcuts import get_object_or_404

logger = get_task_logger(__name__)


@task(name="process_ge_data")
def process_ge_data(uuid):
    process_temp_data(GeData, uuid)

    
@task(name="process_philips_data")
def process_philips_data(uuid):
    process_temp_data(PhilipsData, uuid)

    
@task(name="process_ismrmrd_data")
def process_ismrmrd_data(uuid):
    process_temp_data(IsmrmrdData, uuid)

    
@task(name="process_siemens_data")
def process_siemens_data(uuid):
    process_temp_data(SiemensData, uuid)

    
def process_temp_data(dtype, uuid):

    temp_data = get_object_or_404(dtype, uuid=uuid)
    uploader = temp_data.uploader
    data = Data()
    
    try:
        convert_temp_data_to_data(temp_data, dtype, data)
        upload_to_media(data.ismrmrd_file.name)
    except Exception as e:
        raise_temp_data_error(temp_data, traceback.format_exc())
        set_uploader_refresh(uploader)
        raise e
        
    try:
        parse_ismrmrd(data)
    except Exception as e:
        raise_temp_data_error(temp_data, traceback.format_exc())
        set_uploader_refresh(uploader)
        raise e

    try:
        create_thumbnail(data)
        upload_to_media(data.thumbnail_file.name)
    except Exception as e:
        pass

    data.save()
    temp_data.delete()
    set_uploader_refresh(uploader)


def convert_ge_data(uuid):
    ismrmrd_file = os.path.join(settings.TEMP_ROOT, '{}.h5'.format(uuid))
    ge_pfile = os.path.join(settings.TEMP_ROOT, 'P{}.7'.format(uuid))

    if not os.path.exists(ge_pfile):
        raise IOError('{} does not exists.'.format(ge_pfile))
    
    logger.info('Converting GeData to ISMRMRD')
    subprocess.check_output(['ge_to_ismrmrd',
                             '--verbose',
                             '-o', ismrmrd_file,
                             ge_pfile])
    logger.info('Conversion SUCCESS')


def convert_siemens_data(uuid):
    ismrmrd_file = os.path.join(settings.TEMP_ROOT, '{}.h5'.format(uuid))
    siemens_dat_file = os.path.join(settings.TEMP_ROOT, '{}.dat'.format(uuid))
    
    if not os.path.exists(siemens_dat_file):
        raise IOError('{} does not exists.'.format(siemens_dat_file))
    
    logger.info('Converting SiemensData to ISMRMRD...')
    subprocess.check_output(['siemens_to_ismrmrd',
                             '-f', siemens_dat_file,
                             '-o', ismrmrd_file])
    logger.info('Conversion SUCCESS')


def convert_philips_data(uuid):
    
    philips_basename = os.path.join(settings.TEMP_ROOT, str(uuid))
    schema_file = os.path.join(settings.STATICFILES_DIRS[0], 'schema', 'ismrmrd_philips.xsl')
    ismrmrd_file = os.path.join(settings.TEMP_ROOT, '{}.h5'.format(uuid))
    
    logger.info('Converting PhilipsData to ISMRMRD')
    subprocess.check_output(['philips_to_ismrmrd',
                             '-f', philips_basename,
                             '-x', schema_file,
                             '-o', ismrmrd_file])
    logger.info('Conversion SUCCESS')


def convert_temp_data_to_data(temp_data, dtype, data):
    
    data.uuid = temp_data.uuid
    data.uploader_id = temp_data.uploader_id
    data.upload_date = temp_data.upload_date
    data.anatomy = temp_data.anatomy
    data.fullysampled = temp_data.fullysampled
    data.references = temp_data.references
    data.comments = temp_data.comments

    if dtype == GeData:
        convert_ge_data(temp_data.uuid)
    elif dtype == SiemensData:
        convert_siemens_data(temp_data.uuid)
    elif dtype == PhilipsData:
        convert_philips_data(temp_data.uuid)

    data.ismrmrd_file = '{}.h5'.format(temp_data.uuid)


def set_uploader_refresh(uploader):
    
    uploader.refresh = True
    uploader.save()

    
def raise_temp_data_error(temp_data, error_message):
    
    temp_data.failed = True
    temp_data.error_message = error_message
    temp_data.save()
    
    
def upload_to_media(fname):
    
    local_file = os.path.join(settings.TEMP_ROOT, fname)
    if not os.path.exists(local_file):
        raise IOError('{} does not exists.'.format(local_file))

    if settings.USE_AWS:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

        media_file = os.path.join(settings.AWS_MEDIA_LOCATION, fname)
        bucket.upload_file(local_file, media_file, ExtraArgs={'ACL': 'public-read'})
    else:
        media_file = os.path.join(settings.MEDIA_ROOT, fname)
        shutil.copyfile(local_file, media_file)

        
def parse_ismrmrd(data):
    
    local_ismrmrd_file = os.path.join(settings.TEMP_ROOT, data.ismrmrd_file.name)
    
    if not os.path.exists(local_ismrmrd_file):
        raise IOError('{} does not exists.'.format(local_ismrmrd_file))

    logger.info('Parsing ISMRMRD...')

    dset = ismrmrd.Dataset(local_ismrmrd_file, 'dataset', create_if_needed=False)
    hdr = ismrmrd.xsd.CreateFromDocument(dset.read_xml_header())

    try:
        data.sequence_name = hdr.measurementInformation.protocolName
    except Exception:
        pass

    try:
        data.number_of_channels = hdr.acquisitionSystemInformation.receiverChannels
    except Exception:
        pass
        
    try:
        data.scanner_vendor = hdr.acquisitionSystemInformation.systemVendor
    except Exception:
        pass
        
    try:
        data.scanner_model = hdr.acquisitionSystemInformation.systemModel
    except Exception:
        pass
    
    try:
        data.scanner_field = hdr.acquisitionSystemInformation.systemFieldStrength_T
    except Exception:
        pass

    try:
        data.tr = hdr.sequenceParameters.TR[0]
    except Exception:
        pass
    
    try:
        data.te = hdr.sequenceParameters.TE[0]
    except Exception:
        pass
    
    try:
        data.ti = hdr.sequenceParameters.TI[0]
    except Exception:
        pass
    
    try:
        data.flip_angle = hdr.sequenceParameters.flipAngle_deg[0]
    except Exception:
        pass

    try:
        data.trajectory = hdr.encoding[0].trajectory
    except Exception:
        pass
    
    try:
        data.matrix_size_x = hdr.encoding[0].encodedSpace.matrixSize.x
    except Exception:
        pass
    
    try:
        data.matrix_size_y = hdr.encoding[0].encodedSpace.matrixSize.y
    except Exception:
        pass
    
    try:
        data.matrix_size_z = hdr.encoding[0].encodedSpace.matrixSize.z
    except Exception:
        pass
    
    try:
        data.resolution_x = hdr.encoding[0].encodedSpace.fieldOfView_mm.x / data.matrix_size_x
    except Exception:
        pass
    
    try:
        data.resolution_y = hdr.encoding[0].encodedSpace.fieldOfView_mm.y / data.matrix_size_y
    except Exception:
        pass
    
    try:
        data.resolution_z = hdr.encoding[0].encodedSpace.fieldOfView_mm.z / data.matrix_size_z
    except Exception:
        pass
    
    try:
        data.number_of_slices = hdr.encoding[0].encodingLimits.slice.maximum + 1
    except Exception:
        pass
        
    try:
        data.number_of_repetitions = hdr.encoding[0].encodingLimits.repetition.maximum + 1
    except Exception:
        pass
        
    try:
        data.number_of_contrasts = hdr.encoding[0].encodingLimits.contrast.maximum + 1
    except Exception:
        pass
        
    logger.info('Parse SUCCESS')


def create_thumbnail(data):

    local_ismrmrd_file = os.path.join(settings.TEMP_ROOT, data.ismrmrd_file.name)
    if not os.path.exists(local_ismrmrd_file):
        raise IOError('{} does not exists.'.format(local_ismrmrd_file))

    dset = ismrmrd.Dataset(local_ismrmrd_file, 'dataset', create_if_needed=False)
    hdr = ismrmrd.xsd.CreateFromDocument(dset.read_xml_header())
    logger.info('Creating thumbnail...')

    enc = hdr.encoding[0]
    nx = enc.encodedSpace.matrixSize.x
    ny = enc.encodedSpace.matrixSize.y
    nz = enc.encodedSpace.matrixSize.z

    ncoils = hdr.acquisitionSystemInformation.receiverChannels
    if enc.encodingLimits.slice is not None:
        nslices = enc.encodingLimits.slice.maximum + 1
    else:
        nslices = 1

    if enc.encodingLimits.repetition is not None:
        nreps = enc.encodingLimits.repetition.maximum + 1
    else:
        nreps = 1

    if enc.encodingLimits.contrast is not None:
        ncontrasts = enc.encodingLimits.contrast.maximum + 1
    else:
        ncontrasts = 1

    NZ = 64
    NY = 128
    NX = 128
    ksp = np.zeros([ncoils, min(nz, NZ), min(ny, NY), min(nx, NX)], dtype=np.complex64)
    logger.info('Reading k-space...')
    for acqnum in range(dset.number_of_acquisitions()):
        acq = dset.read_acquisition(acqnum)
        if acq.isFlagSet(ismrmrd.ACQ_IS_NOISE_MEASUREMENT):
            continue

        rep = acq.idx.repetition
        contrast = acq.idx.contrast
        slice = acq.idx.slice
        if (rep == nreps // 2 and contrast == ncontrasts // 2 and slice == nslices // 2):
            y = acq.idx.kspace_encode_step_1 - max(ny - NY, 0) // 2
            z = acq.idx.kspace_encode_step_2 - max(nz - NZ, 0) // 2
            if (y >= 0 and y < NY) and (z >= 0 and z < NZ):
                ksp[:, z, y, :] = crop(acq.data, [ncoils, min(nx, NX)])
    logger.info('Finished reading k-space.')

    logger.info('Transforming k-space...')
    ksp_mix = ifftc(ksp, axes=[-3])
    slice_energy = rss(ksp_mix, axes=(-1, -2, -4))
    ksp_slice = ksp_mix[:, np.argmax(slice_energy), :, :]
    img_slice = rss(ifftc(ksp_slice, axes=[-1, -2]))
    img_slice = crop(img_slice, [min(ny, NY), min(nx, NX)])
    logger.info('Finished transforming k-space.')
    
    thumbnail = zpad(img_slice, [NY, NX]).T
    thumbnail = thumbnail / np.percentile(thumbnail, 99)
    thumbnail = np.clip(thumbnail, 0, 1) * 255
    thumbnail = thumbnail.astype(np.uint8)

    # Save
    thumbnail_file = '{}.png'.format(data.uuid)
    pil = Image.fromarray(thumbnail)
    pil.save(os.path.join(settings.TEMP_ROOT, thumbnail_file))

    logger.info('Thumbnail creation SUCCESS')
    data.thumbnail_file = thumbnail_file
