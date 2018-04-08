from django import forms
from registration.forms import RegistrationForm
from .models import Data, PhilipsData, SiemensData, GeData, IsmrmrdData


class DataForm(forms.ModelForm):

    class Meta:
        model = Data
        fields = ('project_name',
                  'anatomy',
                  'fullysampled',
                  'references',
                  'comments',
                  'thumbnail_file',
        )
        widgets = {
            'references': forms.Textarea(attrs={'rows':3, 'cols':50}),
            'comments': forms.Textarea(attrs={'rows':3, 'cols':50}),
        }
        

class PhilipsDataForm(forms.ModelForm):
    
    philips_lab_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    philips_raw_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    philips_sin_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = PhilipsData
        fields = (
            'anatomy',
            'fullysampled',
            'project_name',
            'references',
            'comments',
            'philips_lab_file',
            'philips_raw_file',
            'philips_sin_file',
            'thumbnail_horizontal_flip',
            'thumbnail_vertical_flip',
            'thumbnail_transpose',
            'thumbnail_fftshift_along_z',
        )
        widgets = {
            'references': forms.Textarea(attrs={'rows':3, 'cols':50}),
            'comments': forms.Textarea(attrs={'rows':3, 'cols':50}),
        }


class GeDataForm(forms.ModelForm):
    
    ge_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = GeData
        fields = [
            'anatomy',
            'fullysampled',
            'project_name',
            'references',
            'comments',
            'ge_file',
            'thumbnail_horizontal_flip',
            'thumbnail_vertical_flip',
            'thumbnail_transpose',
            'thumbnail_fftshift_along_z',
        ]
        widgets = {
            'references': forms.Textarea(attrs={'rows':3, 'cols':50}),
            'comments': forms.Textarea(attrs={'rows':3, 'cols':50}),
        }


class SiemensDataForm(forms.ModelForm):

    siemens_dat_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    
    class Meta:
        model = SiemensData
        fields = (
            'anatomy',
            'fullysampled',
            'project_name',
            'references',
            'comments',
            'siemens_dat_file',
            'thumbnail_horizontal_flip',
            'thumbnail_vertical_flip',
            'thumbnail_transpose',
            'thumbnail_fftshift_along_z',
        )
        widgets = {
            'references': forms.Textarea(attrs={'rows':3, 'cols':50}),
            'comments': forms.Textarea(attrs={'rows':3, 'cols':50}),
        }

        
class IsmrmrdDataForm(forms.ModelForm):
    
    ismrmrd_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = IsmrmrdData
        fields = (
            'anatomy',
            'fullysampled',
            'project_name',
            'references',
            'comments',
            'ismrmrd_file',
            'thumbnail_horizontal_flip',
            'thumbnail_vertical_flip',
            'thumbnail_transpose',
            'thumbnail_fftshift_along_z',
        )
        widgets = {
            'references': forms.Textarea(attrs={'rows':3, 'cols':50}),
            'comments': forms.Textarea(attrs={'rows':3, 'cols':50}),
        }
