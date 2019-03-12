from celery.decorators import task
from celery.utils.log import get_task_logger

import os
import shutil
import traceback
import ismrmrd
import subprocess
import numpy as np
import boto3
import zipfile
from io import BytesIO

from .recon import ifftc, rss, resize
from .models import Data, PhilipsData, SiemensData, GeData, IsmrmrdData, Log, \
    PhilipsAwsData, SiemensAwsData, GeAwsData, IsmrmrdAwsData
from PIL import Image
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404

logger = get_task_logger(__name__)

@task(name="process_ge_data")
def process_ge_data(uuid):
    if settings.USE_AWS:
        process_temp_data(GeAwsData, uuid)
    else:
        process_temp_data(GeData, uuid)


@task(name="process_philips_data")
def process_philips_data(uuid):
    if settings.USE_AWS:
        process_temp_data(PhilipsAwsData, uuid)
    else:
        process_temp_data(PhilipsData, uuid)


@task(name="process_ismrmrd_data")
def process_ismrmrd_data(uuid):
    if settings.USE_AWS:
        process_temp_data(IsmrmrdAwsData, uuid)
    else:
        process_temp_data(IsmrmrdData, uuid)


@task(name="process_siemens_data")
def process_siemens_data(uuid):
    if settings.USE_AWS:
        process_temp_data(SiemensAwsData, uuid)
    else:
        process_temp_data(SiemensData, uuid)



def log(string, uploader):
    Log(string=string, user=uploader.user).save()
    logger.info(string)
    set_uploader_refresh(uploader)


def process_temp_data(dtype, uuid):

    temp_data = get_object_or_404(dtype, uuid=uuid)
    uploader = temp_data.uploader
    data = Data()

    log("{} backend processing started.".format(str(temp_data)[37:]), uploader)

    convert_data(temp_data, dtype, data)

    parse_ismrmrd(temp_data, data)
    create_thumbnail(temp_data, data)

    ismrmrd_file = '{}.h5'.format(temp_data.uuid)
    upload_temp_file_to_media(ismrmrd_file)
    data.save()

    log("{} backend processing completed. UUID is {}.".format(str(temp_data)[37:],
                                                              temp_data.uuid), uploader)
    temp_data.delete()


def convert_ge_data(temp_data):
    ismrmrd_file = '{}.h5'.format(temp_data.uuid)
    ge_file = str(temp_data)
    get_upload_file_to_temp(ge_file)

    subprocess.check_output(['ge_to_ismrmrd',
                             '--verbose',
                             '-o', os.path.join(settings.TEMP_ROOT, ismrmrd_file),
                             os.path.join(settings.TEMP_ROOT, ge_file)])

    os.remove(os.path.join(settings.TEMP_ROOT, ge_file))


def convert_siemens_data(temp_data):
    ismrmrd_file = '{}.h5'.format(temp_data.uuid)
    siemens_dat_file = str(temp_data)
    get_upload_file_to_temp(siemens_dat_file)

    # Get last measurement number
    stdout = subprocess.run(['siemens_to_ismrmrd',
                             '-f', os.path.join(settings.TEMP_ROOT, siemens_dat_file),
                             '-H', '-o', os.path.join(settings.TEMP_ROOT, ismrmrd_file)],
                            stdout=subprocess.PIPE).stdout
    start = stdout.find(b'This file contains ') + len('This file contains ')
    end = stdout.find(b' measurement(s)')
    meas_num = stdout[start:end].decode("utf-8")

    subprocess.check_output(['siemens_to_ismrmrd',
                             '-f', os.path.join(settings.TEMP_ROOT, siemens_dat_file),
                             '-o', os.path.join(settings.TEMP_ROOT, ismrmrd_file), '-z', meas_num])

    os.remove(os.path.join(settings.TEMP_ROOT, siemens_dat_file))


def convert_philips_data(temp_data):
    philips_lab_file = str(temp_data.philips_lab_file).split("/")[-1]
    philips_sin_file = str(temp_data.philips_sin_file).split("/")[-1]
    philips_raw_file = str(temp_data.philips_raw_file).split("/")[-1]
    schema_file = os.path.join(settings.STATICFILES_DIRS[0], 'schema', 'ismrmrd_philips.xsl')
    ismrmrd_file = '{}.h5'.format(temp_data.uuid)

    get_upload_file_to_temp(philips_lab_file)
    get_upload_file_to_temp(philips_sin_file)
    get_upload_file_to_temp(philips_raw_file)

    subprocess.check_output(['philips_to_ismrmrd',
                             '-f', os.path.join(settings.TEMP_ROOT,
                                                os.path.splitext(philips_lab_file)[0]),
                             '-x', schema_file,
                             '-o', os.path.join(settings.TEMP_ROOT, ismrmrd_file)])

    os.remove(os.path.join(settings.TEMP_ROOT, philips_lab_file))
    os.remove(os.path.join(settings.TEMP_ROOT, philips_sin_file))
    os.remove(os.path.join(settings.TEMP_ROOT, philips_raw_file))


def convert_ismrmrd_data(temp_data):
    ismrmrd_file = '{}.h5'.format(temp_data.uuid)
    temp_ismrmrd_file = str(temp_data)
    get_upload_file_to_temp(temp_ismrmrd_file)

    os.rename(os.path.join(settings.TEMP_ROOT, temp_ismrmrd_file),
              os.path.join(settings.TEMP_ROOT, ismrmrd_file))


def convert_data(temp_data, dtype, data):
    try:
        data.ismrmrd_file = '{}.h5'.format(temp_data.uuid)
        data.uuid = temp_data.uuid
        data.uploader_id = temp_data.uploader_id
        data.upload_date = temp_data.upload_date
        data.anatomy = temp_data.anatomy
        data.project = temp_data.project
        data.fullysampled = temp_data.fullysampled
        data.references = temp_data.references
        data.comments = temp_data.comments
        data.funding_support = temp_data.funding_support
        data.thumbnail_horizontal_flip = data.thumbnail_horizontal_flip
        data.thumbnail_vertical_flip = data.thumbnail_vertical_flip
        data.thumbnail_transpose = data.thumbnail_transpose

        if dtype in [GeData, GeAwsData]:
            convert_ge_data(temp_data)
        elif dtype in [SiemensData, SiemensAwsData]:
            convert_siemens_data(temp_data)
        elif dtype in [PhilipsData, PhilipsAwsData]:
            convert_philips_data(temp_data)
        elif dtype in [IsmrmrdData, IsmrmrdAwsData]:
            convert_ismrmrd_data(temp_data)

        log("{} ISMRMRD conversion completed. Extracting parameters.".format(str(temp_data)[37:]),
            temp_data.uploader)

    except Exception as e:
        log("{} ISMRMRD conversion failed.\n{}".format(
            temp_data, traceback.format_exc()), temp_data.uploader)
        cleanup_temp_data(temp_data)
        raise e


def set_uploader_refresh(uploader):
    uploader.refresh = True
    uploader.save()


def cleanup_temp_data(temp_data):
    if os.path.exists(os.path.join(settings.TEMP_ROOT, str(temp_data))):
        os.remove(os.path.join(settings.TEMP_ROOT, str(temp_data)))

    temp_data.delete()


def get_upload_file_to_temp(file):
    if settings.USE_AWS:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

        key = os.path.join(settings.AWS_MEDIA_LOCATION, 'uploads/', file)
        upload_file = bucket.Object(key)
        upload_file.download_file(os.path.join(settings.TEMP_ROOT, file))
        upload_file.delete()
    else:
        upload_file = os.path.join(settings.MEDIA_ROOT, 'uploads', file)
        shutil.move(upload_file, os.path.join(settings.TEMP_ROOT, file))


def upload_temp_file_to_media(file):

    if not os.path.exists(os.path.join(settings.TEMP_ROOT, file)):
        raise IOError('{} does not exists.'.format(file))

    if settings.USE_AWS:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

        key = os.path.join(settings.AWS_MEDIA_LOCATION, file)
        media_file = bucket.Object(key)
        media_file.upload_file(os.path.join(settings.TEMP_ROOT, file),
                               ExtraArgs={'ACL': 'public-read'})
        os.remove(os.path.join(settings.TEMP_ROOT, file))
    else:
        media_file = os.path.join(settings.MEDIA_ROOT, file)
        shutil.move(os.path.join(settings.TEMP_ROOT, file), media_file)


def parse_ismrmrd(temp_data, data):

    try:
        ismrmrd_file = '{}.h5'.format(temp_data.uuid)
        dset = ismrmrd.Dataset(os.path.join(settings.TEMP_ROOT, ismrmrd_file),
                               'dataset', create_if_needed=False)
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

        log("{} parameter extraction completed. Generating thumbnail.".format(str(temp_data)[37:]),
            temp_data.uploader)

    except Exception as e:
        log("{} parameter extraction failed.\n{}".format(
            temp_data, traceback.format_exc()), temp_data.uploader)
        cleanup_temp_data(temp_data)
        raise e


def create_thumbnail(temp_data, data):
    '''
    Based on:
    https://github.com/ismrmrd/ismrmrd-python-tools/blob/master/recon_ismrmrd_dataset.py
    '''

    try:
        ismrmrd_file = '{}.h5'.format(temp_data.uuid)
        dset = ismrmrd.Dataset(os.path.join(settings.TEMP_ROOT, ismrmrd_file),
                               'dataset', create_if_needed=False)

        hdr = ismrmrd.xsd.CreateFromDocument(dset.read_xml_header())

        try:
            if hdr.acquisitionSystemInformation.receiverChannels is not None:
                number_of_channels = hdr.acquisitionSystemInformation.receiverChannels
            else:
                number_of_channels = 1
        except Exception:
            number_of_channels = 1

        try:
            matrix_size_x = hdr.encoding[0].encodedSpace.matrixSize.x
        except Exception:
            matrix_size_x = 1

        try:
            matrix_size_y = hdr.encoding[0].encodedSpace.matrixSize.y
        except Exception:
            matrix_size_y = 1

        try:
            recon_matrix_size_x = hdr.encoding[0].reconSpace.matrixSize.x
        except Exception:
            recon_matrix_size_x = matrix_size_x

        try:
            recon_matrix_size_y = hdr.encoding[0].reconSpace.matrixSize.y
        except Exception:
            recon_matrix_size_y = matrix_size_y

        try:
            matrix_size_z = hdr.encoding[0].encodedSpace.matrixSize.z
        except Exception:
            matrix_size_z = 1

        try:
            number_of_averages = hdr.encoding[0].encodingLimits.average.maximum + 1
        except Exception:
            number_of_averages = 1

        try:
            number_of_slices = hdr.encoding[0].encodingLimits.slice.maximum + 1
        except Exception:
            number_of_slices = 1

        try:
            number_of_repetitions = hdr.encoding[0].encodingLimits.repetition.maximum + 1
        except Exception:
            number_of_repetitions = 1

        try:
            number_of_contrasts = hdr.encoding[0].encodingLimits.contrast.maximum + 1
        except Exception:
            number_of_contrasts = 1

        try:
            number_of_phases = hdr.encoding[0].encodingLimits.phase.maximum + 1
        except Exception:
            number_of_phases = 1

        try:
            number_of_segments = hdr.encoding[0].encodingLimits.segment.maximum + 1
        except Exception:
            number_of_segments = 1

        try:
            number_of_sets = hdr.encoding[0].encodingLimits.set.maximum + 1
        except Exception:
            number_of_sets = 1

        try:
            field_of_view_x = hdr.encoding[0].encodedSpace.fieldOfView_mm.x
        except Exception:
            field_of_view_x = 1

        try:
            field_of_view_y = hdr.encoding[0].encodedSpace.fieldOfView_mm.y
        except Exception:
            field_of_view_y = 1

        try:
            system_vendor = hdr.acquisitionSystemInformation.systemVendor
        except Exception:
            system_vendor = ''

        GE = 'GE' in system_vendor

        energy = np.zeros([number_of_slices, number_of_repetitions,
                           number_of_contrasts, number_of_phases, number_of_sets])
        for acqnum in range(dset.number_of_acquisitions()):
            acq = dset.read_acquisition(acqnum)
            if acq.isFlagSet(ismrmrd.ACQ_IS_NOISE_MEASUREMENT):
                continue

            y = acq.idx.kspace_encode_step_1
            z = acq.idx.kspace_encode_step_2

            if z >= 0 and z < matrix_size_z and y >= 0 and y < matrix_size_y:
                try:
                    energy[acq.idx.slice, acq.idx.repetition,
                           acq.idx.contrast, acq.idx.phase,
                           acq.idx.set] = np.sum(np.abs(acq.data)**2)
                except:
                    pass

        slice_idx, repetition_idx, contrast_idx, phase_idx, set_idx = np.where(
            energy == energy.max())

        ksp = np.zeros([number_of_channels, matrix_size_z, matrix_size_y, matrix_size_x],
                       dtype=np.complex64)
        for acqnum in range(dset.number_of_acquisitions()):
            acq = dset.read_acquisition(acqnum)
            if acq.isFlagSet(ismrmrd.ACQ_IS_NOISE_MEASUREMENT):
                continue

            if (acq.idx.slice == slice_idx and
                acq.idx.repetition == repetition_idx and
                acq.idx.contrast == contrast_idx and
                acq.idx.phase == phase_idx and
                acq.idx.set == set_idx):

                y = acq.idx.kspace_encode_step_1
                z = acq.idx.kspace_encode_step_2

                if z >= 0 and z < matrix_size_z and y >= 0 and y < matrix_size_y:
                    ksp[:, z, y, :] = acq.data

        z_idx = np.argmax(np.sum(np.abs(ksp)**2, axis=(0, 2, 3)))
        ksp_slice = ksp[:, z_idx, :, :]

        cimg_slice = rss(ifftc(ksp_slice, axes=[-2, -1]))
        if not GE:
            cimg_slice = resize(cimg_slice, [recon_matrix_size_y, recon_matrix_size_x])

        thumbnail = cimg_slice.T
        thumbnail = thumbnail / np.percentile(thumbnail, 99)
        thumbnail = np.clip(thumbnail, 0, 1) * 255
        thumbnail = thumbnail.astype(np.uint8)

        res_x = field_of_view_x / matrix_size_x
        res_y = field_of_view_y / matrix_size_y
        min_res = min(res_x, res_y)

        pil = Image.fromarray(thumbnail)
        pil = pil.resize([int(thumbnail.shape[0] * res_x / min_res),
                          int(thumbnail.shape[1] * res_y / min_res)], resample=3)

        thumbnail_file = '{}.jpg'.format(temp_data.uuid)
        pil.save(os.path.join(settings.TEMP_ROOT, thumbnail_file))
        upload_temp_file_to_media(thumbnail_file)

        data.thumbnail_file = thumbnail_file

        log("{} thumbnail generation completed. Uploading to storage.".format(
            str(temp_data)[37:]), temp_data.uploader)

    except Exception as e:
        log("{} thumbnail generation failed.\n{}".format(
            temp_data, traceback.format_exc()), temp_data.uploader)
