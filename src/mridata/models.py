import os
import uuid
import boto3
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from s3direct.fields import S3DirectField


class Project(models.Model):

    name = models.CharField(max_length=100, default='')
    
    def __str__(self):
        return self.name


class Uploader(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    refresh = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.__str__()


class Data(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)

    anatomy = models.CharField(max_length=100, default='Unknown')
    fullysampled = models.NullBooleanField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    references = models.TextField(blank=True, default='')
    comments = models.TextField(blank=True, default='')
    funding_support = models.TextField(blank=True, default='')
    
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

    thumbnail_file = models.ImageField()
    
    ismrmrd_file = models.FileField(verbose_name='ISMRMRD File')
    
    upload_date = models.DateTimeField(default=timezone.now)
    uploader = models.ForeignKey(Uploader, on_delete=models.CASCADE)
    downloads = models.IntegerField(default=0)

    def __str__(self):
        return str(self.uuid)

    def delete(self, *args, **kwargs):
        if settings.USE_AWS:
            try:
                delete_aws_file('{}.png'.format(self.uuid))
                delete_aws_file('{}.h5'.format(self.uuid))
            except:
                pass
                
        if len(self.project.data_set.all()) == 1:
            self.project.delete()
            
        super().delete(*args, **kwargs)


class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_time = models.DateTimeField(default=timezone.now)
    string = models.TextField(blank=True)

    def __str__(self):
        return self.string


class TempData(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    anatomy = models.CharField(max_length=100, default='Unknown')
    fullysampled = models.NullBooleanField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    references = models.TextField(blank=True, default='')
    comments = models.TextField(blank=True, default='')
    funding_support = models.TextField(blank=True, default='')

    original_filename = models.TextField(default='')
    
    upload_date = models.DateTimeField(default=timezone.now)
    uploader = models.ForeignKey(Uploader, on_delete=models.CASCADE)
    
    thumbnail_horizontal_flip = models.BooleanField(default=False)
    thumbnail_vertical_flip = models.BooleanField(default=False)
    thumbnail_transpose = models.BooleanField(default=False)

    def __str__(self):
        return str(self.uuid)
    
    def delete(self, *args, **kwargs):
        if len(self.project.data_set.all()) == 0:
            self.project.delete()
            
        super().delete(*args, **kwargs)
        

class PhilipsData(TempData):
    philips_raw_file = models.FileField(upload_to='uploads/')
    philips_sin_file = models.FileField(upload_to='uploads/')
    philips_lab_file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return str(self.philips_raw_file).split('/')[-1]

    def delete(self, *args, **kwargs):
        self.philips_raw_file.delete()
        self.philips_sin_file.delete()
        self.philips_lab_file.delete()
        super().delete(*args, **kwargs)
        

class PhilipsAwsData(TempData):
    philips_raw_file = S3DirectField(dest='uploads')
    philips_sin_file = S3DirectField(dest='uploads')
    philips_lab_file = S3DirectField(dest='uploads')

    def __str__(self):
        return str(self.philips_raw_file).split('/')[-1]

    def delete(self, *args, **kwargs):
        delete_aws_file(os.path.join('uploads/', str(self.philips_raw_file)))
        delete_aws_file(os.path.join('uploads/', str(self.philips_sin_file)))
        delete_aws_file(os.path.join('uploads/', str(self.philips_lab_file)))
        super().delete(*args, **kwargs)

        
class SiemensData(TempData):
    siemens_dat_file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return str(self.siemens_dat_file).split('/')[-1]

    def delete(self, *args, **kwargs):
        self.siemens_dat_file.delete()
        super().delete(*args, **kwargs)

        
class SiemensAwsData(TempData):
    siemens_dat_file = S3DirectField(dest='uploads')

    def __str__(self):
        return str(self.siemens_dat_file).split('/')[-1]

    def delete(self, *args, **kwargs):
        delete_aws_file(os.path.join('uploads/', str(self.siemens_dat_file)))
        super().delete(*args, **kwargs)

        
class GeData(TempData):
    ge_file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return str(self.ge_file).split('/')[-1]

    def delete(self, *args, **kwargs):
        self.ge_file.delete()
        super().delete(*args, **kwargs)

        
class GeAwsData(TempData):
    ge_aws_file = S3DirectField(dest='uploads')

    def __str__(self):
        return str(self.ge_file).split('/')[-1]

    def delete(self, *args, **kwargs):
        delete_aws_file(os.path.join('uploads/', str(self.ge_file)))
        super().delete(*args, **kwargs)

        
class IsmrmrdData(TempData):
    ismrmrd_file = models.FileField(upload_to='uploads/', blank=True)

    def __str__(self):
        return str(self.ismrmrd_file).split('/')[-1]

    def delete(self, *args, **kwargs):
        self.ismrmrd_file.delete()
        super().delete(*args, **kwargs)

        
class IsmrmrdAwsData(TempData):
    ismrmrd_file = S3DirectField(dest='uploads')

    def __str__(self):
        return str(self.ismrmrd_file).split('/')[-1]

    def delete(self, *args, **kwargs):
        delete_aws_file(os.path.join('uploads/', str(self.ismrmrd_file)))
        super().delete(*args, **kwargs)
        
        
def create_uploader(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        uploader = Uploader(user=user)
        uploader.save()

        
post_save.connect(create_uploader, sender=User)


def delete_aws_file(filename):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

    key = os.path.join(settings.AWS_MEDIA_LOCATION, filename)
    upload_file = bucket.Object(key).delete()


def save_ismrmrd_file(data, filename):
    filename = 'temp_{}.h5'.format(data.uuid)
    return filename


def save_philips_raw_file(data, filename):
    filename = 'temp_{}.raw'.format(data.uuid)
    return filename


def save_philips_sin_file(data, filename):
    filename = 'temp_{}.sin'.format(data.uuid)
    return filename


def save_philips_lab_file(data, filename):
    filename = 'temp_{}.lab'.format(data.uuid)
    return filename


def save_siemens_dat_file(data, filename):
    filename = 'temp_{}.dat'.format(data.uuid)
    return filename


def save_ge_file(data, filename):
    if os.path.splitext(filename)[-1] == '.h5':
        filename = 'temp_{}.h5'.format(data.uuid)
    else:
        filename = 'Ptemp_{}.7'.format(data.uuid)
    return filename

