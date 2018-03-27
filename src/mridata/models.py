import os
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save


def save_ismrmrd_file(data, filename):
    filename = '{}.h5'.format(data.uuid)
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


def save_ge_file(data, filename):
    if os.path.splitext(filename)[-1] == '.h5':
        filename = '{}.h5'.format(data.uuid)
    else:
        filename = 'P{}.7'.format(data.uuid)
    return filename


class Uploader(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    refresh = models.BooleanField(default=False)
    
    def __str__(self):

        return self.user.__str__()


class Data(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)

    anatomy = models.CharField(max_length=100, default='Unknown')
    fullysampled = models.NullBooleanField()
    
    protocol_name = models.CharField(max_length=100, default='', blank=True)
    series_description = models.TextField(default='', blank=True)
    
    system_vendor = models.CharField(max_length=100, default='', blank=True)
    system_model = models.CharField(max_length=100, default='', blank=True)
    system_field_strength = models.FloatField(verbose_name='Field Strength [T]', default=-1)
    relative_receiver_noise_bandwidth = models.FloatField(default=-1)
    number_of_channels = models.IntegerField(default=-1)
    coil_name= models.CharField(max_length=100, default='', blank=True)
    institution_name = models.CharField(max_length=100, default='', blank=True)
    station_name = models.CharField(max_length=100, default='', blank=True)
    
    h1_resonance_frequency = models.FloatField(verbose_name='H1 Resonance Frequency [Hz]',
                                               default=-1)
    matrix_size_x = models.IntegerField(default=-1)
    matrix_size_y = models.IntegerField(default=-1)
    matrix_size_z = models.IntegerField(default=-1)
    
    field_of_view_x = models.FloatField(verbose_name='Field of View x [mm]', default=-1)
    field_of_view_y = models.FloatField(verbose_name='Field of View y [mm]', default=-1)
    field_of_view_z = models.FloatField(verbose_name='field of View z [mm]', default=-1)
    
    number_of_averages = models.IntegerField(default=-1)
    number_of_slices = models.IntegerField(default=-1)
    number_of_repetitions = models.IntegerField(default=-1)
    number_of_contrasts = models.IntegerField(default=-1)
    number_of_phases = models.IntegerField(default=-1)
    number_of_sets = models.IntegerField(default=-1)
    number_of_segments = models.IntegerField(default=-1)
    
    trajectory = models.CharField(max_length=100, default='', blank=True)
    parallel_imaging_factor_y = models.FloatField(default=-1)
    parallel_imaging_factor_z = models.FloatField(default=-1)
    echo_train_length = models.IntegerField(default=-1)
    
    tr = models.FloatField(verbose_name='Repetition Time [ms]', default=-1)
    te = models.FloatField(verbose_name='Echo Time [ms]', default=-1)
    ti = models.FloatField(verbose_name='Inversion Time [ms]', default=-1)
    flip_angle = models.FloatField(verbose_name='Flip Angle [degree]', default=-1)
    sequence_type = models.CharField(max_length=100, default='', blank=True)
    echo_spacing = models.FloatField(verbose_name='Echo Spacing [ms]', default=-1)
    
    references = models.TextField(blank=True, default='')
    comments = models.TextField(blank=True, default='')

    thumbnail_file = models.ImageField()
    thumbnail_horizontal_flip = models.BooleanField(default=False)
    thumbnail_vertical_flip = models.BooleanField(default=False)
    thumbnail_rotate_90_degree = models.BooleanField(default=False)
    
    ismrmrd_file = models.FileField(upload_to=save_ismrmrd_file,
                                    verbose_name='ISMRMRD File')
    
    upload_date = models.DateTimeField(default=timezone.now)
    uploader = models.ForeignKey(Uploader, on_delete=models.CASCADE)

    
temp_storage = FileSystemStorage(location=settings.TEMP_ROOT, base_url=settings.TEMP_URL)


class TempData(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    anatomy = models.CharField(max_length=100, default='Unknown')
    fullysampled = models.NullBooleanField()
    
    references = models.TextField(blank=True, default='')
    comments = models.TextField(blank=True, default='')
    
    upload_date = models.DateTimeField(default=timezone.now)
    uploader = models.ForeignKey(Uploader, on_delete=models.CASCADE)
    
    thumbnail_horizontal_flip = models.BooleanField(default=False)
    thumbnail_vertical_flip = models.BooleanField(default=False)
    thumbnail_rotate_90_degree = models.BooleanField(default=False)
    
    failed = models.NullBooleanField(default=False)
    error_message = models.TextField(blank=True)

class PhilipsData(TempData):
    
    philips_raw_file = models.FileField(upload_to=save_philips_raw_file,
                                        storage=temp_storage)
    philips_sin_file = models.FileField(upload_to=save_philips_sin_file,
                                        storage=temp_storage)
    philips_lab_file = models.FileField(upload_to=save_philips_lab_file,
                                        storage=temp_storage)

    def delete(self, *args, **kwargs):

        self.philips_raw_file.delete()
        self.philips_sin_file.delete()
        self.philips_lab_file.delete()
        super().delete(*args, **kwargs)

class SiemensData(TempData):
    
    siemens_dat_file = models.FileField(upload_to=save_siemens_dat_file,
                                        storage=temp_storage)

    def delete(self, *args, **kwargs):

        self.siemens_dat_file.delete()
        super().delete(*args, **kwargs)

        
class GeData(TempData):

    ge_file = models.FileField(upload_to=save_ge_file,
                               storage=temp_storage)

    def delete(self, *args, **kwargs):

        self.ge_file.delete()
        super().delete(*args, **kwargs)

        
class IsmrmrdData(TempData):
    
    ismrmrd_file = models.FileField(upload_to=save_ismrmrd_file,
                                    storage=temp_storage)

    def delete(self, *args, **kwargs):

        self.ismrmrd_file.delete()
        super().delete(*args, **kwargs)

        
def create_uploader(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        uploader = Uploader(user=user)
        uploader.save()

        
post_save.connect(create_uploader, sender=User)
