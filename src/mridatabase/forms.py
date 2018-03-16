from django import forms
from .models import Data, PhilipsData, SiemensData, GeData, IsmrmrdData

    
class DataForm(forms.ModelForm):

    class Meta:
        model = Data
        fields = ('anatomy',
                  'fullysampled',
                  'sequence_name',
                  'trajectory',
                  'matrix_size_x',
                  'matrix_size_y',
                  'matrix_size_z',
                  'number_of_channels',
                  'number_of_slices',
                  'number_of_repetitions',
                  'number_of_contrasts',
                  'resolution_x',
                  'resolution_y',
                  'resolution_z',
                  'flip_angle',
                  'te',
                  'tr',
                  'ti',
                  'thumbnail_file',
                  'ismrmrd_file',
        )
        

class PhilipsDataForm(forms.ModelForm):

    class Meta:
        model = PhilipsData
        fields = (
            'anatomy',
            'fullysampled',
            'philips_lab_file',
            'philips_raw_file',
            'philips_sin_file',
        )
        
        labels = {
            'anatomy' : 'Anatomy',
            'fullysampled' : 'Fullysampled',
            'philips_lab_file' : 'Philips LAB-File',
            'philips_raw_file' : 'Philips RAW-File',
            'philips_sin_file' : 'Philips SIN-File'
            }


class GeDataForm(forms.ModelForm):

    class Meta:
        model = GeData
        fields = [
            'anatomy',
            'fullysampled',
            'ge_pfile',
            ]
        labels = {
            'anatomy' : 'Anatomy',
            'fullysampled' : 'Fullysampled',
            'ge_pfile' : 'GE P-File'
            }


class SiemensDataForm(forms.ModelForm):

    class Meta:
        model = SiemensData
        fields = (
            'anatomy',
            'fullysampled',
            'siemens_dat_file',
        )
        labels = {
            'anatomy' : 'Anatomy',
            'fullysampled' : 'Fullysampled',
            'siemens_dat_file' : 'Siemens DAT-File'
            }

        
class IsmrmrdDataForm(forms.ModelForm):

    class Meta:
        model = IsmrmrdData
        fields = (
            'anatomy',
            'fullysampled',
            'ismrmrd_file',
        )
        labels = {
            'anatomy' : 'Anatomy',
            'fullysampled' : 'Fullysampled',
            'ismrmrd_file' : 'ISMRMRD File'
            }
