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


def save_ge_pfile(data, filename):
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
    sequence_name = models.CharField(max_length=100, default='N/A')
    trajectory = models.CharField(max_length=100, default='N/A')
    fullysampled = models.NullBooleanField()
    
    scanner_vendor = models.CharField(max_length=100, default='N/A')
    scanner_model = models.CharField(max_length=100, default='N/A')
    scanner_field = models.FloatField(verbose_name='Field Strength [T]', default=-1)
    
    matrix_size_x = models.IntegerField(default=-1)
    matrix_size_y = models.IntegerField(default=-1)
    matrix_size_z = models.IntegerField(default=-1)
    number_of_channels = models.IntegerField(default=-1)
    number_of_slices = models.IntegerField(default=-1)
    number_of_repetitions = models.IntegerField(default=-1)
    number_of_contrasts = models.IntegerField(default=-1)
    
    resolution_x = models.FloatField(verbose_name='Resolution x [mm]', default=-1)
    resolution_y = models.FloatField(verbose_name='Resolution y [mm]', default=-1)
    resolution_z = models.FloatField(verbose_name='Resolution z [mm]', default=-1)
    
    flip_angle = models.FloatField(verbose_name='Flip Angle [degree]', default=-1)
    te = models.FloatField(verbose_name='Echo Time [ms]', default=-1)
    tr = models.FloatField(verbose_name='Repetition Time [ms]', default=-1)
    ti = models.FloatField(verbose_name='Inversion Time [ms]', default=-1)
    
    references = models.TextField(blank=True, default='')
    comments = models.TextField(blank=True, default='')
    
    ismrmrd_file = models.FileField(upload_to=save_ismrmrd_file,
                                    verbose_name='ISMRMRD File')

    thumbnail_file = models.ImageField()
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

    ge_pfile = models.FileField(upload_to=save_ge_pfile,
                                storage=temp_storage)

    def delete(self, *args, **kwargs):

        self.ge_pfile.delete()
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
