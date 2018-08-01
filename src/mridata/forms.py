import logging
from django import forms
from registration.forms import RegistrationForm
from .models import Data, PhilipsData, SiemensData, GeData, IsmrmrdData, Project


class DataForm(forms.ModelForm):

    project_name = forms.CharField()
    
    class Meta:
        model = Data
        fields = ('project_name',
                  'anatomy',
                  'fullysampled',
                  'references',
                  'comments',
                  'funding_support',
                  'thumbnail_file',
        )
        widgets = {
            'references': forms.Textarea(attrs={'rows':3, 'cols':50}),
            'comments': forms.Textarea(attrs={'rows':3, 'cols':50}),
            'funding_support': forms.Textarea(attrs={'rows':3, 'cols':50}),
        }
        

class PhilipsDataForm(forms.ModelForm):
    
    project_name = forms.CharField()
    philips_lab_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    philips_raw_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    philips_sin_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = PhilipsData
        fields = (
            'project_name',
            'anatomy',
            'fullysampled',
            'references',
            'comments',
            'funding_support',
            'philips_lab_file',
            'philips_raw_file',
            'philips_sin_file',
            'thumbnail_horizontal_flip',
            'thumbnail_vertical_flip',
            'thumbnail_transpose',
        )
        widgets = {
            'references': forms.Textarea(attrs={'rows':3, 'cols':50}),
            'comments': forms.Textarea(attrs={'rows':3, 'cols':50}),
        }


class GeDataForm(forms.ModelForm):
    
    project_name = forms.CharField()
    ge_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = GeData
        fields = [
            'project_name',
            'anatomy',
            'fullysampled',
            'references',
            'comments',
            'funding_support',
            'ge_file',
            'thumbnail_horizontal_flip',
            'thumbnail_vertical_flip',
            'thumbnail_transpose',
        ]
        widgets = {
            'references': forms.Textarea(attrs={'rows':3, 'cols':50}),
            'comments': forms.Textarea(attrs={'rows':3, 'cols':50}),
            'funding_support': forms.Textarea(attrs={'rows':3, 'cols':50}),
        }


class SiemensDataForm(forms.ModelForm):

    project_name = forms.CharField()
    siemens_dat_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    
    class Meta:
        model = SiemensData
        fields = (
            'project_name',
            'anatomy',
            'fullysampled',
            'references',
            'comments',
            'funding_support',
            'siemens_dat_file',
            'thumbnail_horizontal_flip',
            'thumbnail_vertical_flip',
            'thumbnail_transpose',
        )
        widgets = {
            'references': forms.Textarea(attrs={'rows':3, 'cols':50}),
            'comments': forms.Textarea(attrs={'rows':3, 'cols':50}),
            'funding_support': forms.Textarea(attrs={'rows':3, 'cols':50}),
        }

        
class IsmrmrdDataForm(forms.ModelForm):
    
    project_name = forms.CharField()
    ismrmrd_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = IsmrmrdData
        fields = (
            'project_name',
            'anatomy',
            'fullysampled',
            'references',
            'comments',
            'funding_support',
            'ismrmrd_file',
            'thumbnail_horizontal_flip',
            'thumbnail_vertical_flip',
            'thumbnail_transpose',
        )
        widgets = {
            'references': forms.Textarea(attrs={'rows':3, 'cols':50}),
            'comments': forms.Textarea(attrs={'rows':3, 'cols':50}),
            'funding_support': forms.Textarea(attrs={'rows':3, 'cols':50}),
        }
