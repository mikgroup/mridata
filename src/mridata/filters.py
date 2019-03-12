import django_filters
from django import forms

from .models import Data


class DataFilter(django_filters.FilterSet):
    # ADD AutoComplete
    search = django_filters.CharFilter(label='Search', field_name='search',
                                       lookup_expr='icontains',
                                       widget=forms.TextInput(attrs={
                                           'size': 12,
                                           'class' :'form-control input-lg',
                                           'placeholder': 'Search',
                                           'id': 'txtSearch',
                                           'name': 'txtSearch'
                                       }))

    uploader = django_filters.CharFilter(label='Uploader', field_name='uploader__user__username',
                                         lookup_expr='icontains',
                                         widget=forms.TextInput(attrs={'size': 12}))
    project = django_filters.CharFilter(label='Project', field_name='project__name',
                                        lookup_expr='icontains',
                                        widget=forms.TextInput(attrs={'size': 12}))
    anatomy = django_filters.CharFilter(label='Anatomy', lookup_expr='icontains',
                                        widget=forms.TextInput(attrs={'size': 12}))
    references = django_filters.CharFilter(label='References', lookup_expr='icontains',
                                           widget=forms.TextInput(attrs={'size': 12}))
    comments = django_filters.CharFilter(label='Comments', lookup_expr='icontains',
                                         widget=forms.TextInput(attrs={'size': 12}))
    tags = django_filters.CharFilter(label='Tags', lookup_expr='icontains',
                                     widget=forms.TextInput(attrs={'size': 12}))

    funding_support = django_filters.CharFilter(label='Funding Support', lookup_expr='icontains',
                                                widget=forms.TextInput(attrs={'size': 12}))
    system_vendor = django_filters.CharFilter(label='System Vendor', lookup_expr='icontains',
                                              widget=forms.TextInput(attrs={'size': 12}))
    system_model = django_filters.CharFilter(label='System Model', lookup_expr='icontains',
                                             widget=forms.TextInput(attrs={'size': 12}))
    protocol_name = django_filters.CharFilter(label='Protocol Name', lookup_expr='icontains',
                                              widget=forms.TextInput(attrs={'size': 12}))
    coil_name = django_filters.CharFilter(label='Coil Name', lookup_expr='icontains',
                                          widget=forms.TextInput(attrs={'size': 12}))
    sequence_type = django_filters.CharFilter(label='Sequence Type', lookup_expr='icontains',
                                              widget=forms.TextInput(attrs={'size': 12}))
    uuid = django_filters.CharFilter(label='UUID', lookup_expr='icontains',
                                     widget=forms.TextInput(attrs={'size': 12}))

    class Meta:
        model = Data
        fields = ['fullysampled',
                  'uploader',]
