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
                  'references',
                  'comments',
                  'thumbnail_file',
                  'ismrmrd_file',
        )
        widgets = {
          'references': forms.Textarea(attrs={'rows':3, 'cols':30}),
          'comments': forms.Textarea(attrs={'rows':3, 'cols':30}),
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
            'references',
            'comments',
            'philips_lab_file',
            'philips_raw_file',
            'philips_sin_file',
        )
        widgets = {
          'references': forms.Textarea(attrs={'rows':3, 'cols':30}),
          'comments': forms.Textarea(attrs={'rows':3, 'cols':30}),
        }


class GeDataForm(forms.ModelForm):
    
    ge_pfile = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = GeData
        fields = [
            'anatomy',
            'fullysampled',
            'references',
            'comments',
            'ge_pfile',
        ]
        widgets = {
          'references': forms.Textarea(attrs={'rows':3, 'cols':30}),
          'comments': forms.Textarea(attrs={'rows':3, 'cols':30}),
        }


class SiemensDataForm(forms.ModelForm):

    siemens_dat_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    
    class Meta:
        model = SiemensData
        fields = (
            'anatomy',
            'fullysampled',
            'references',
            'comments',
            'siemens_dat_file',
        )
        widgets = {
          'references': forms.Textarea(attrs={'rows':3, 'cols':30}),
          'comments': forms.Textarea(attrs={'rows':3, 'cols':30}),
        }

        
class IsmrmrdDataForm(forms.ModelForm):
    
    ismrmrd_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = IsmrmrdData
        fields = (
            'anatomy',
            'fullysampled',
            'references',
            'comments',
            'ismrmrd_file',
        )
        widgets = {
          'references': forms.Textarea(attrs={'rows':3, 'cols':30}),
          'comments': forms.Textarea(attrs={'rows':3, 'cols':30}),
        }
