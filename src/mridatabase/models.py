from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.conf import settings

import uuid


def validate_cfl_file(value):
    if not value.name.endswith('.cfl'):
        raise ValidationError(u'File does not end with .cfl')

def validate_hdr_file(value):
    if not value.name.endswith('.hdr'):
        raise ValidationError(u'File does not end with .hdr')

def validate_ra_file(value):
    if not value.name.endswith('.ra'):
        raise ValidationError(u'File does not end with .ra')
    
def validate_ismrmrd_file(value):
    if not value.name.endswith('.h5'):
        raise ValidationError(u'File does not end with .h5')
    
def validate_philips_raw_file(value):
    if not value.name.endswith('.raw'):
        raise ValidationError(u'File does not end with .raw')
    
def validate_philips_sin_file(value):
    if not value.name.endswith('.sin'):
        raise ValidationError(u'File does not end with .sin')
    
def validate_philips_lab_file(value):
    if not value.name.endswith('.lab'):
        raise ValidationError(u'File does not end with .lab')
    
def validate_siemens_dat_file(value):
    if not value.name.endswith('.dat'):
        raise ValidationError(u'File does not end with .dat')

def save_ismrmrd_file(data, filename):
    filename = '{}.h5'.format(data.uuid)
    return filename

def save_cfl_file(data, filename):
    filename = '{}.cfl'.format(data.uuid)
    return filename

def save_hdr_file(data, filename):
    filename = '{}.hdr'.format(data.uuid)
    return filename

def save_ra_file(data, filename):
    filename = '{}.ra'.format(data.uuid)
    return filename

def save_philips_raw_file(data, filename):
    filename = '{}.raw'.format(data.uuid)
    return filename

def save_philips_sin_file(data, filename):
    filename = '{}.sin'.format(data.uuid)
    return filename

def save_philips_lab_file(data, filename):
    filename = '{}.lab'.format(data.uuid)
    return filename

def save_siemens_dat_file(data, filename):
    filename = '{}.dat'.format(data.uuid)
    return filename

def save_ge_pfile(data, filename):
    filename = 'P{}.7'.format(data.uuid)
    return filename


class Data(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)

    anatomy = models.CharField(max_length=100, default='N/A')
    sequence_name = models.CharField(max_length=100, default='N/A')
    trajectory = models.CharField(max_length=100, default='N/A')
    fullysampled = models.BooleanField()
    
    scanner_vendor = models.CharField(max_length=100, default='N/A')
    scanner_model = models.CharField(max_length=100, default='N/A', blank=True)
    scanner_field = models.FloatField(verbose_name='Field Strength [T]',
                                      default=-1, blank=True)
    
    matrix_size_x = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    matrix_size_y = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    matrix_size_z = models.PositiveIntegerField(validators=[MinValueValidator(0)],
                                                default=1)
    number_of_channels = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    number_of_slices = models.PositiveIntegerField(validators=[MinValueValidator(0)],
                                                   default=1)
    number_of_repetitions = models.PositiveIntegerField(validators=[MinValueValidator(0)],
                                                        default=1)
    number_of_contrasts = models.PositiveIntegerField(validators=[MinValueValidator(0)],
                                                      default=1)
    
    resolution_x = models.FloatField(verbose_name='Resolution x [mm]',
                                     validators=[MinValueValidator(0)])
    resolution_y = models.FloatField(verbose_name='Resolution y [mm]',
                                     validators=[MinValueValidator(0)])
    resolution_z = models.FloatField(verbose_name='Resolution z [mm]',
                                     validators=[MinValueValidator(0)])
    
    flip_angle = models.FloatField(verbose_name='Flip Angle [degree]',
                                   validators=[MinValueValidator(0)])
    te = models.FloatField(verbose_name='Echo Time [ms]',
                           validators=[MinValueValidator(0)])
    tr = models.FloatField(verbose_name='Repetition Time [ms]',
                           validators=[MinValueValidator(0)])
    ti = models.FloatField(verbose_name='Inversion Time [ms]',
                           validators=[MinValueValidator(0)], default=0)
    
    ismrmrd_file = models.FileField(upload_to=save_ismrmrd_file,
                                    verbose_name='ISMRMRD File',
                                    validators=[validate_ismrmrd_file])

    thumbnail_file = models.ImageField()
    upload_date = models.DateTimeField(default=timezone.now)
    uploader = models.ForeignKey(User)


temp_storage = FileSystemStorage(location=settings.TEMP_ROOT, base_url=settings.TEMP_URL)

class TempData(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    anatomy = models.CharField(max_length=100)
    fullysampled = models.BooleanField()
    
    upload_date = models.DateTimeField(default=timezone.now)
    uploader = models.ForeignKey(User)

    failed = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)

class PhilipsData(TempData):
    
    philips_raw_file = models.FileField(upload_to=save_philips_raw_file,
                                        validators=[validate_philips_raw_file],
                                        storage=temp_storage)
    philips_sin_file = models.FileField(upload_to=save_philips_sin_file,
                                        validators=[validate_philips_sin_file],
                                        storage=temp_storage)
    philips_lab_file = models.FileField(upload_to=save_philips_lab_file,
                                        validators=[validate_philips_lab_file],
                                        storage=temp_storage)

    def delete(self, *args, **kwargs):

        self.philips_raw_file.delete()
        self.philips_sin_file.delete()
        self.philips_lab_file.delete()
        super().delete(*args, **kwargs)

class SiemensData(TempData):
    
    siemens_dat_file = models.FileField(upload_to=save_siemens_dat_file,
                                        validators=[validate_siemens_dat_file],
                                        storage=temp_storage)

    def delete(self, *args, **kwargs):

        self.siemens_dat_file.delete()
        super().delete(*args, **kwargs)

class GeData(TempData):

    ge_pfile = models.FileField(upload_to=save_ge_pfile,
                                storage=temp_storage)

    def delete(self, *args, **kwargs):

        self.ge_pfile.delete()
        super().delete(*args, **kwargs)

class IsmrmrdData(TempData):
    
    ismrmrd_file = models.FileField(upload_to=save_ismrmrd_file,
                                    validators=[validate_ismrmrd_file],
                                    storage=temp_storage)

    def delete(self, *args, **kwargs):

        self.ismrmrd_file.delete()
        super().delete(*args, **kwargs)

class CflData(Data):
    
    cfl_file = models.FileField(upload_to=save_cfl_file,
                                validators=[validate_cfl_file],
                                storage=temp_storage)
    hdr_file = models.FileField(upload_to=save_hdr_file,
                                validators=[validate_hdr_file],
                                storage=temp_storage)

    def delete(self, *args, **kwargs):

        self.cfl_file.delete()
        self.hdr_file.delete()
        super().delete(*args, **kwargs)

class RaData(Data):
    
    ra_file = models.FileField(upload_to=save_ra_file,
                               validators=[validate_ra_file],
                               storage=temp_storage)

    def delete(self, *args, **kwargs):

        self.ra_file.delete()
        super().delete(*args, **kwargs)
