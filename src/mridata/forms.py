from django import forms
from registration.forms import RegistrationForm
from .models import Data, PhilipsData, SiemensData, GeData, IsmrmrdData


class DataForm(forms.ModelForm):

    class Meta:
        model = Data
        fields = ('anatomy',
                  'fullysampled',
                  
                  'protocol_name',
                  'series_description',
                  
                  'system_vendor',
                  'system_model',
                  'system_field_strength',
                  'relative_receiver_noise_bandwidth',
                  'number_of_channels',
                  'coil_name',
                  'institution_name',
                  'station_name',
                  
                  'h1_resonance_frequency',
                  
                  'matrix_size_x',
                  'matrix_size_y',
                  'matrix_size_z',
                  
                  'field_of_view_x',
                  'field_of_view_y',
                  'field_of_view_z',
                  
                  'number_of_averages',
                  'number_of_slices',
                  'number_of_repetitions',
                  'number_of_contrasts',
                  'number_of_phases',
                  'number_of_sets',
                  'number_of_segments',
                  
                  'trajectory',
                  'parallel_imaging_factor_y',
                  'parallel_imaging_factor_z',
                  'echo_train_length',
                  
                  'tr',
                  'te',
                  'ti',
                  'flip_angle',
                  'sequence_type',
                  'echo_spacing',
                  
                  'references',
                  'comments',
                  
                  'thumbnail_file',
                  'thumbnail_horizontal_flip',
                  'thumbnail_vertical_flip',
                  'thumbnail_rotate_90_degree',
                  
                  'ismrmrd_file',
        )
        widgets = {
            'series_description': forms.Textarea(attrs={'rows':3, 'cols':30}),
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
            'thumbnail_horizontal_flip',
            'thumbnail_vertical_flip',
            'thumbnail_rotate_90_degree',
        )
        widgets = {
            'references': forms.Textarea(attrs={'rows':3, 'cols':30}),
            'comments': forms.Textarea(attrs={'rows':3, 'cols':30}),
        }


class GeDataForm(forms.ModelForm):
    
    ge_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = GeData
        fields = [
            'anatomy',
            'fullysampled',
            'references',
            'comments',
            'ge_file',
            'thumbnail_horizontal_flip',
            'thumbnail_vertical_flip',
            'thumbnail_rotate_90_degree',
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
            'thumbnail_horizontal_flip',
            'thumbnail_vertical_flip',
            'thumbnail_rotate_90_degree',
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
            'thumbnail_horizontal_flip',
            'thumbnail_vertical_flip',
            'thumbnail_rotate_90_degree',
        )
        widgets = {
            'references': forms.Textarea(attrs={'rows':3, 'cols':30}),
            'comments': forms.Textarea(attrs={'rows':3, 'cols':30}),
        }
