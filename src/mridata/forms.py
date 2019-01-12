import logging
from django import forms
from django.conf import settings
from registration.forms import RegistrationForm
from .models import Data, PhilipsData, SiemensData, GeData, IsmrmrdData, Project, \
    PhilipsAwsData, SiemensAwsData, GeAwsData, IsmrmrdAwsData
from s3direct.widgets import S3DirectWidget
from django.utils.safestring import mark_safe



class DataForm(forms.ModelForm):

    project_name = forms.CharField(label="Project Name", required=True)
    fullysampled = forms.NullBooleanField(label="Fully Sampled")
    funding_support = forms.CharField(label="Funding Support", required=True)

    class Meta:
        model = Data
        fields = ('project_name',
                  'anatomy',
                  'fullysampled',
                  'references',
                  'comments',
                  'funding_support',
                  'thumbnail_file',
                  'thumbnail_horizontal_flip',
                  'thumbnail_vertical_flip',
                  'thumbnail_transpose',
        )
        widgets = {
            'references': forms.Textarea(attrs={'rows':2, 'cols':50}),
            'comments': forms.Textarea(attrs={'rows':2, 'cols':50}),
            'funding_support': forms.Textarea(attrs={'rows':2, 'cols':50}),
        }


class PhilipsDataForm(forms.ModelForm):

    project_name = forms.CharField(label="Project Name", required=True)
    fullysampled = forms.NullBooleanField(label="Fully Sampled")
    funding_support = forms.CharField(label="Funding Support", required=True)

    if settings.USE_AWS:
        philips_lab_file = forms.URLField(widget=S3DirectWidget(dest='uploads'), label="Philips Lab File")
        philips_raw_file = forms.URLField(widget=S3DirectWidget(dest='uploads'), label="Philips Raw File")
        philips_sin_file = forms.URLField(widget=S3DirectWidget(dest='uploads'), label="Philips Sin File")
    else:
        philips_lab_file = forms.FileField(widget=forms.ClearableFileInput(), label="Philips Lab File")
        philips_raw_file = forms.FileField(widget=forms.ClearableFileInput(), label="Philips Raw File")
        philips_sin_file = forms.FileField(widget=forms.ClearableFileInput(), label="Philips Sin File")

    class Meta:
        if settings.USE_AWS:
            model = PhilipsAwsData
        else:
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
            'references': forms.Textarea(attrs={'rows':2, 'cols':50}),
            'comments': forms.Textarea(attrs={'rows':2, 'cols':50}),
            'funding_support': forms.Textarea(attrs={'rows':2, 'cols':50}),
        }


class GeDataForm(forms.ModelForm):

    project_name = forms.CharField(label="Project Name", required=True)
    fullysampled = forms.NullBooleanField(label="Fully Sampled")
    funding_support = forms.CharField(label="Funding Support", required=True)

    if settings.USE_AWS:
        ge_file = forms.URLField(widget=S3DirectWidget(dest='uploads'), label="GE File")
    else:
        ge_file = forms.FileField(widget=forms.ClearableFileInput(), label="GE File")

    class Meta:
        if settings.USE_AWS:
            model = GeAwsData
        else:
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
            'references': forms.Textarea(attrs={'rows':2, 'cols':50}),
            'comments': forms.Textarea(attrs={'rows':2, 'cols':50}),
            'funding_support': forms.Textarea(attrs={'rows':2, 'cols':50}),
            'tags': forms.Textarea(attrs={'rows':1, 'cols':50}),
        }


class SiemensDataForm(forms.ModelForm):

    project_name = forms.CharField(label="Project Name", required=True)
    fullysampled = forms.NullBooleanField(label="Fully Sampled")
    funding_support = forms.CharField(label="Funding Support", required=True)

    if settings.USE_AWS:
        siemens_dat_file = forms.URLField(widget=S3DirectWidget(dest='uploads'), label="Siemens File")
    else:
        siemens_dat_file = forms.FileField(widget=forms.ClearableFileInput(), label="Siemens File")

    class Meta:
        if settings.USE_AWS:
            model = SiemensAwsData
        else:
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
            'references': forms.Textarea(attrs={'rows':2, 'cols':50}),
            'comments': forms.Textarea(attrs={'rows':2, 'cols':50}),
            'funding_support': forms.Textarea(attrs={'rows':2, 'cols':50}),
        }


class IsmrmrdDataForm(forms.ModelForm):

    project_name = forms.CharField(label="Project Name", required=True)
    fullysampled = forms.NullBooleanField(label="Fully Sampled")
    funding_support = forms.CharField(label="Funding Support", required=True)

    if settings.USE_AWS:
        ismrmrd_file = forms.URLField(widget=S3DirectWidget(dest='uploads'), label='ISMRMRD File')
    else:
        ismrmrd_file = forms.FileField(widget=forms.ClearableFileInput(), label='ISMRMRD File')

    class Meta:
        if settings.USE_AWS:
            model = IsmrmrdAwsData
        else:
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
            'references': forms.Textarea(attrs={'rows':2, 'cols':50}),
            'comments': forms.Textarea(attrs={'rows':2, 'cols':50}),
            'funding_support': forms.Textarea(attrs={'rows':2, 'cols':50}),
        }
