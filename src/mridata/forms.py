from django import forms
from .models import Data, PhilipsData, SiemensData, GeData, IsmrmrdData
        

class PhilipsDataForm(forms.ModelForm):
    
    philips_lab_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    philips_raw_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    philips_sin_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

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
    
    ge_pfile = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

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

    siemens_dat_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    
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
    
    ismrmrd_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

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
