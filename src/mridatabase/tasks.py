from celery.decorators import task
from celery.utils.log import get_task_logger

import os
import traceback
import ismrmrd
import subprocess
import numpy as np
import boto3
from .recon import ifftc, rss, zpad, crop
from .models import Data, TempData, PhilipsData, SiemensData, GeData, IsmrmrdData
from PIL import Image

from django.conf import settings
from django.shortcuts import get_object_or_404

logger = get_task_logger(__name__)


def convert_ge_data(uuid):
    ismrmrd_file = os.path.join(settings.TEMP_ROOT, '{}.h5'.format(uuid))
    schema_file = os.path.join(settings.STATICFILES_DIRS[0], 'schema', 'ismrmrd_ge.xsl')
    ge_pfile = os.path.join(settings.TEMP_ROOT, 'P{}.7'.format(uuid))
    
    logger.info('Converting GeData to ISMRMRD')
    subprocess.check_output(['pfile2ismrmrd',
                             '-v',
                             '-x', schema_file,
                             '-o', ismrmrd_file,
                             ge_pfile])
    logger.info('Conversion SUCCESS')


def convert_siemens_data(uuid):
    ismrmrd_file = os.path.join(settings.TEMP_ROOT, '{}.h5'.format(uuid))
    siemens_dat_file = os.path.join(settings.TEMP_ROOT, '{}.dat'.format(uuid))
    
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
    try:
        data = Data()
        data.uuid = temp_data.uuid
        data.uploader_id = temp_data.uploader_id
        data.upload_date = temp_data.upload_date
        data.anatomy = temp_data.anatomy
        data.fullysampled = temp_data.fullysampled

        if dtype == GeData:
            convert_ge_data(temp_data.uuid)
        elif dtype == SiemensData:
            convert_siemens_data(temp_data.uuid)
        elif dtype == PhilipsData:
            convert_philips_data(temp_data.uuid)

        ismrmrd_file = '{}.h5'.format(temp_data.uuid)
        temp_ismrmrd_file = os.path.join(settings.TEMP_ROOT, ismrmrd_file)
        parse_ismrmrd(temp_ismrmrd_file, data)

        thumbnail_file = '{}.png'.format(temp_data.uuid)
        temp_thumbnail_file = os.path.join(settings.TEMP_ROOT, thumbnail_file)

        if settings.USE_AWS:
            s3 = boto3.resource('s3')
            bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
            
            media_ismrmrd_file = os.path.join(settings.AWS_MEDIA_LOCATION, ismrmrd_file)
            bucket.upload_file(temp_ismrmrd_file, media_ismrmrd_file,
                               ExtraArgs={'ACL': 'public-read'})
            media_thumbnail_file = os.path.join(settings.AWS_MEDIA_LOCATION, thumbnail_file)
            bucket.upload_file(temp_thumbnail_file, media_thumbnail_file,
                               ExtraArgs={'ACL': 'public-read'})
            os.remove(temp_ismrmrd_file)
            os.remove(temp_thumbnail_file)
        else:
            media_ismrmrd_file = os.path.join(settings.MEDIA_ROOT, ismrmrd_file)
            os.rename(temp_ismrmrd_file, media_ismrmrd_file)
            media_thumbnail_file = os.path.join(settings.MEDIA_ROOT, thumbnail_file)
            os.rename(temp_thumbnail_file, media_thumbnail_file)
            
        data.ismrmrd_file = ismrmrd_file
        data.thumbnail_file = thumbnail_file
        data.save()
        temp_data.delete()
        
    except Exception as e:
        
        temp_data.failed = True
        temp_data.error_message = traceback.format_exc()
        temp_data.save()
        raise e


def valid_float(x):
    try:
        o = np.float(x)
    except ValueError:
        o = 0
    if np.isnan(o):
        o = 0
    return o


def valid_int(x):
    try:
        o = int(float(x))
    except ValueError:
        o = 0
    if np.isnan(o):
        o = 0
    return o

        
def parse_ismrmrd(ismrmrd_file, data):

    logger.info('Parsing ISMRMRD...')

    dset = ismrmrd.Dataset(ismrmrd_file, 'dataset', create_if_needed=False)
    hdr = ismrmrd.xsd.CreateFromDocument(dset.read_xml_header())

    data.sequence_name = hdr.measurementInformation.protocolName
    data.number_of_channels = hdr.acquisitionSystemInformation.receiverChannels
    data.scanner_vendor = hdr.acquisitionSystemInformation.systemVendor
    if hdr.acquisitionSystemInformation.systemModel is not None:
        data.scanner_model = hdr.acquisitionSystemInformation.systemModel
    if hdr.acquisitionSystemInformation.systemModel is not None:
        data.scanner_field = hdr.acquisitionSystemInformation.systemFieldStrength_T

    data.tr = hdr.sequenceParameters.TR[0]
    data.te = hdr.sequenceParameters.TE[0]
    data.ti = hdr.sequenceParameters.TI[0]
    data.flip_angle = hdr.sequenceParameters.flipAngle_deg[0]

    data.trajectory = hdr.encoding[0].trajectory
    data.matrix_size_x = hdr.encoding[0].encodedSpace.matrixSize.x
    data.matrix_size_y = hdr.encoding[0].encodedSpace.matrixSize.y
    data.matrix_size_z = hdr.encoding[0].encodedSpace.matrixSize.z
    data.resolution_x = hdr.encoding[0].encodedSpace.fieldOfView_mm.x / data.matrix_size_x
    data.resolution_y = hdr.encoding[0].encodedSpace.fieldOfView_mm.y / data.matrix_size_y
    data.resolution_z = hdr.encoding[0].encodedSpace.fieldOfView_mm.z / data.matrix_size_z
    try:
        if hdr.encoding[0].encodedSpace.slice is not None:
            data.number_of_slices = hdr.encoding[0].encodedSpace.slice.maximum + 1
    except:
        pass
    try:
        if hdr.encoding[0].encodedSpace.repetition is not None:
            data.number_of_repetitions = hdr.encoding[0].encodedSpace.repetition.maximum + 1
    except:
        pass
    try:
        if hdr.encoding[0].encodedSpace.contrast is not None:
            data.number_of_contrasts = hdr.encoding[0].encodedSpace.contrast.maximum + 1
    except:
        pass
        
    logger.info('Parse SUCCESS')
    create_thumbnail(dset, hdr, data)


def create_thumbnail(dset, hdr, data):

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
    
    thumbnail = zpad(img_slice, [NY,
                                 NX]).T
    thumbnail = thumbnail / np.percentile(thumbnail, 99)
    thumbnail = np.clip(thumbnail, 0, 1) * 255
    thumbnail = thumbnail.astype(np.uint8)

    # Save
    thumbnail_file = '{}.png'.format(data.uuid)
    pil = Image.fromarray(thumbnail)
    pil.save(os.path.join(settings.TEMP_ROOT, thumbnail_file))

    logger.info('Thumbnail creation SUCCESS')
