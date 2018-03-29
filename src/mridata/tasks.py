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

    try:
        upload_to_media(data.ismrmrd_file.name)
    except Exception as e:
        raise_temp_data_error(temp_data, traceback.format_exc())
        set_uploader_refresh(uploader)
        raise e

    data.save()
    temp_data.delete()
    set_uploader_refresh(uploader)


def convert_ge_data(uuid):
    ismrmrd_file = '{}.h5'.format(uuid)
    try:
        ge_file = 'P{}.7'.format(uuid)
        download_from_media(ge_file)
    except Exception:
        ge_file = '{}_archive.h5'.format(uuid)
        download_from_media(ge_file)
    
    logger.info('Converting GeData to ISMRMRD')
    subprocess.check_output(['ge_to_ismrmrd',
                             '--verbose',
                             '-o', ismrmrd_file,
                             ge_file])
    logger.info('Conversion SUCCESS')

    os.remove(ge_file)


def convert_siemens_data(uuid):
    ismrmrd_file = '{}.h5'.format(uuid)
    siemens_dat_file = '{}.dat'.format(uuid)
    
    download_from_media(siemens_dat_file)

    # Get last measurement number
    stdout = subprocess.run(['siemens_to_ismrmrd', '-f', siemens_dat_file,
                             '-H', '-o', ismrmrd_file],
                            stdout=subprocess.PIPE).stdout
    start = stdout.find(b'This file contains ') + len('This file contains ')
    end = stdout.find(b' measurement(s)')
    meas_num = stdout[start:end].decode("utf-8") 
    
    logger.info('Converting SiemensData to ISMRMRD...')
    subprocess.check_output(['siemens_to_ismrmrd',
                             '-f', siemens_dat_file,
                             '-o', ismrmrd_file, '-z', meas_num])
    logger.info('Conversion SUCCESS')

    os.remove(siemens_dat_file)

def convert_philips_data(uuid):
    
    philips_lab_file = '{}.lab'.format(uuid)
    philips_sin_file = '{}.sin'.format(uuid)
    philips_raw_file = '{}.raw'.format(uuid)
    schema_file = os.path.join(settings.STATICFILES_DIRS[0], 'schema', 'ismrmrd_philips.xsl')
    ismrmrd_file = '{}.h5'.format(uuid)
    
    download_from_media(philips_lab_file)
    download_from_media(philips_sin_file)
    download_from_media(philips_raw_file)
    
    logger.info('Converting PhilipsData to ISMRMRD')
    subprocess.check_output(['philips_to_ismrmrd',
                             '-f', str(uuid),
                             '-x', schema_file,
                             '-o', ismrmrd_file])
    logger.info('Conversion SUCCESS')
    
    os.remove(philips_lab_file)
    os.remove(philips_sin_file)
    os.remove(philips_raw_file)


def convert_temp_data_to_data(temp_data, dtype, data):
    
    data.uuid = temp_data.uuid
    data.uploader_id = temp_data.uploader_id
    data.upload_date = temp_data.upload_date
    data.anatomy = temp_data.anatomy
    data.fullysampled = temp_data.fullysampled
    data.references = temp_data.references
    data.comments = temp_data.comments
    data.thumbnail_horizontal_flip = temp_data.thumbnail_horizontal_flip
    data.thumbnail_vertical_flip = temp_data.thumbnail_vertical_flip
    data.thumbnail_rotate_90_degree = temp_data.thumbnail_rotate_90_degree

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

    if os.path.exists('P{}.7'.format(temp_data.uuid)):
        os.remove('P{}.7'.format(temp_data.uuid))
    if os.path.exists('{}_archive.h5'.format(temp_data.uuid)):
        os.remove('{}_archive.h5'.format(temp_data.uuid))
    if os.path.exists('{}.dat'.format(temp_data.uuid)):
        os.remove('{}.dat'.format(temp_data.uuid))
    if os.path.exists('{}.lab'.format(temp_data.uuid)):
        os.remove('{}.lab'.format(temp_data.uuid))
    if os.path.exists('{}.sin'.format(temp_data.uuid)):
        os.remove('{}.sin'.format(temp_data.uuid))
    if os.path.exists('{}.raw'.format(temp_data.uuid)):
        os.remove('{}.raw'.format(temp_data.uuid))
    if os.path.exists('{}.h5'.format(temp_data.uuid)):
        os.remove('{}.h5'.format(temp_data.uuid))        
        
    
def download_from_media(file):

    if settings.USE_AWS:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

        key = os.path.join(settings.AWS_MEDIA_LOCATION, file)
        media_file = bucket.Object(key)
        media_file.download_file(file)
        media_file.delete()
    else:
        media_file = os.path.join(settings.MEDIA_ROOT, file)
        shutil.move(media_file, file)
    
    
def upload_to_media(file):
    
    if not os.path.exists(file):
        raise IOError('{} does not exists.'.format(file))

    if settings.USE_AWS:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

        key = os.path.join(settings.AWS_MEDIA_LOCATION, file)
        media_file = bucket.Object(key)
        media_file.upload_file(file, ExtraArgs={'ACL': 'public-read'})
        os.remove(file)
    else:
        media_file = os.path.join(settings.MEDIA_ROOT, file)
        shutil.move(file, media_file)

        
def parse_ismrmrd(data):
    
    ismrmrd_file = data.ismrmrd_file.name
    
    if not os.path.exists(ismrmrd_file):
        raise IOError('{} does not exists.'.format(ismrmrd_file))

    logger.info('Parsing ISMRMRD...')

    dset = ismrmrd.Dataset(ismrmrd_file, 'dataset', create_if_needed=False)
    hdr = ismrmrd.xsd.CreateFromDocument(dset.read_xml_header())

    try:
        if hdr.measurementInformation.protocolName is not None:
            data.protocol_name = hdr.measurementInformation.protocolName
    except Exception:
        pass
    
    try:
        if hdr.measurementInformation.seriesDescription is not None:
            data.series_description = hdr.measurementInformation.seriesDescription
    except Exception:
        pass
        
    try:
        if hdr.acquisitionSystemInformation.systemVendor is not None:
            data.system_vendor = hdr.acquisitionSystemInformation.systemVendor
    except Exception:
        pass
        
    try:
        if hdr.acquisitionSystemInformation.systemModel is not None:
            data.system_model = hdr.acquisitionSystemInformation.systemModel
    except Exception:
        pass
    
    try:
        if hdr.acquisitionSystemInformation.systemFieldStrength_T is not None:
            data.system_field_strength = hdr.acquisitionSystemInformation.systemFieldStrength_T
    except Exception:
        pass
    
    try:
        if hdr.acquisitionSystemInformation.relativeReceiverNoiseBandwidth is not None:
            data.relative_receiver_noise_bandwidth = hdr.acquisitionSystemInformation.relativeReceiverNoiseBandwidth
    except Exception:
        pass
    
    try:
        if hdr.acquisitionSystemInformation.receiverChannels is not None:
            data.number_of_channels = hdr.acquisitionSystemInformation.receiverChannels
    except Exception:
        pass
    
    try:
        if hdr.acquisitionSystemInformation.coilLabel[0].coilName is not None:
            data.coil_name = hdr.acquisitionSystemInformation.coilLabel[0].coilName
    except Exception:
        pass
    
    try:
        if hdr.acquisitionSystemInformation.institutionName is not None:
            data.institution_name = hdr.acquisitionSystemInformation.institutionName
    except Exception:
        pass
    
    try:
        if hdr.acquisitionSystemInformation.stationName is not None:
            data.station_name = hdr.acquisitionSystemInformation.stationName
    except Exception:
        pass
    
    try:
        if hdr.experimentalConditions.H1reconanceFrequency_Hz is not None:
            data.h1_resonance_frequency = hdr.experimentalConditions.H1reconanceFrequency_Hz
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
        data.field_of_view_x = hdr.encoding[0].encodedSpace.fieldOfView_mm.x
    except Exception:
        pass
    
    try:
        data.field_of_view_y = hdr.encoding[0].encodedSpace.fieldOfView_mm.y
    except Exception:
        pass
    
    try:
        data.field_of_view_z = hdr.encoding[0].encodedSpace.fieldOfView_mm.z
    except Exception:
        pass
    
    try:
        data.number_of_averages = hdr.encoding[0].encodingLimits.average.maximum + 1
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
    
    try:
        data.number_of_phases = hdr.encoding[0].encodingLimits.phase.maximum + 1
    except Exception:
        pass
        
    try:
        data.number_of_sets = hdr.encoding[0].encodingLimits.set.maximum + 1
    except Exception:
        pass
        
    try:
        data.number_of_segments = hdr.encoding[0].encodingLimits.segments.maximum + 1
    except Exception:
        pass

    try:
        if hdr.encoding[0].trajectory is not None:
            data.trajectory = hdr.encoding[0].trajectory
    except Exception:
        pass
    
    try:
        if hdr.encoding[0].parallelImaging.accelerationFactor.kspace_encoding_step_1 is not None:
            data.parallel_imaging_factor_y = hdr.encoding[0].parallelImaging.accelerationFactor.kspace_encoding_step_1
    except Exception:
        pass
    
    try:
        if hdr.encoding[0].parallelImaging.accelerationFactor.kspace_encoding_step_2 is not None:
            data.parallel_imaging_factor_z = hdr.encoding[0].parallelImaging.accelerationFactor.kspace_encoding_step_2
    except Exception:
        pass

    try:
        if hdr.encoding[0].echoTrainLength is not None:
            data.echo_train_length = hdr.encoding[0].echoTrainLength
    except Exception:
        pass

    try:
        if hdr.sequenceParameters.TR[0] is not None:
            data.tr = hdr.sequenceParameters.TR[0]
    except Exception:
        pass
    
    try:
        if hdr.sequenceParameters.TE[0] is not None:
            data.te = hdr.sequenceParameters.TE[0]
    except Exception:
        pass
    
    try:
        if hdr.sequenceParameters.TI[0] is not None:
            data.ti = hdr.sequenceParameters.TI[0]
    except Exception:
        pass
    
    try:
        if hdr.sequenceParameters.flipAngle_deg[0] is not None:
            data.flip_angle = hdr.sequenceParameters.flipAngle_deg[0]
    except Exception:
        pass
    
    try:
        if hdr.sequenceParameters.sequence_type is not None:
            data.sequence_type = hdr.sequenceParameters.sequence_type
    except Exception:
        pass
    
    try:
        if hdr.sequenceParameters.echo_spacing[0] is not None:
            data.echo_spacing = hdr.sequenceParameters.echo_spacing[0]
    except Exception:
        pass
        
    logger.info('Parse SUCCESS')


def make_valid_num(num):
    if num == -1:
        return 1
    else:
        return num


def create_thumbnail(data):
    '''
    Derived from:
    https://github.com/ismrmrd/ismrmrd-python-tools/blob/master/recon_ismrmrd_dataset.py
    '''

    ismrmrd_file = data.ismrmrd_file.name
    if not os.path.exists(ismrmrd_file):
        raise IOError('{} does not exists.'.format(ismrmrd_file))

    dset = ismrmrd.Dataset(ismrmrd_file, 'dataset', create_if_needed=False)
    logger.info('Creating thumbnail...')
    
    header = ismrmrd.xsd.CreateFromDocument(dset.read_xml_header())
    enc = header.encoding[0]
    # Matrix size
    eNx = enc.encodedSpace.matrixSize.x
    eNy = enc.encodedSpace.matrixSize.y
    eNz = enc.encodedSpace.matrixSize.z
    rNx = enc.reconSpace.matrixSize.x

    ncoils = make_valid_num(data.number_of_channels)
    nslices = make_valid_num(data.number_of_slices)
    nreps = make_valid_num(data.number_of_repetitions)
    ncontrasts = make_valid_num(data.number_of_contrasts)

    if rNx < eNx:
        ksp_mix = np.zeros([ncoils, eNz, eNy, rNx], dtype=np.complex64)
    else:
        ksp_mix = np.zeros([ncoils, eNz, eNy, eNx], dtype=np.complex64)
        
    logger.info('Reading k-space...')
    for acqnum in range(dset.number_of_acquisitions()):
        acq = dset.read_acquisition(acqnum)
        if acq.isFlagSet(ismrmrd.ACQ_IS_NOISE_MEASUREMENT):
            continue

        repetition = acq.idx.repetition
        contrast = acq.idx.contrast
        slice = acq.idx.slice
        if repetition == nreps // 2 and contrast == ncontrasts // 2 and slice == nslices // 2:
            y = acq.idx.kspace_encode_step_1
            z = acq.idx.kspace_encode_step_2
            if rNx < eNx:
                ksp_mix[:, z, y, :] = crop(ifftc(acq.data, axes=[-1]), [ncoils, rNx])
            else:
                ksp_mix[:, z, y, :] = ifftc(acq.data, axes=[-1])
                
    logger.info('Finished reading k-space.')

    logger.info('Transforming k-space...')
    ksp_mix = ifftc(ksp_mix, axes=[-3])
    slice_energy = rss(ksp_mix, axes=(-1, -2, -4))
    ksp_mix_slice = ksp_mix[:, np.argmax(slice_energy), :, :]  # choose slice with max energy
    thumbnail = rss(ifftc(ksp_mix_slice, axes=[-2])).T
    logger.info('Finished transforming k-space.')
    
    thumbnail = thumbnail / np.percentile(thumbnail, 99)
    thumbnail = np.clip(thumbnail, 0, 1) * 255
    thumbnail = thumbnail.astype(np.uint8)

    # Save
    thumbnail_file = '{}.png'.format(data.uuid)
    pil = Image.fromarray(thumbnail)
    pil.save(thumbnail_file)

    logger.info('Thumbnail creation SUCCESS')
    data.thumbnail_file = thumbnail_file
