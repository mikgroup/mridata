import django_filters
from django import forms

from .models import Data


class DataFilter(django_filters.FilterSet):

    anatomy = django_filters.CharFilter(label='Anatomy', lookup_expr='icontains',
                                        widget=forms.TextInput(attrs={'size': 12}))
    scanner_vendor = django_filters.CharFilter(label='Scanner Vendor', lookup_expr='icontains',
                                               widget=forms.TextInput(attrs={'size': 12}))
    scanner_model = django_filters.CharFilter(label='Scanner Model', lookup_expr='icontains',
                                              widget=forms.TextInput(attrs={'size': 12}))
    sequence_name = django_filters.CharFilter(label='Sequence Name', lookup_expr='icontains',
                                              widget=forms.TextInput(attrs={'size': 12}))
    uuid = django_filters.CharFilter(label='UUID', lookup_expr='icontains',
                                     widget=forms.TextInput(attrs={'size': 12}))
    references = django_filters.CharFilter(label='References', lookup_expr='icontains',
                                                 widget=forms.TextInput(attrs={'size': 12}))
    comments = django_filters.CharFilter(label='Comments', lookup_expr='icontains',
                                         widget=forms.TextInput(attrs={'size': 12}))

    class Meta:
        model = Data
        fields = ['fullysampled',
                  'uploader']
