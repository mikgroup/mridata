import os
import numpy as np

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse

from django.forms.formsets import formset_factory

from .models import Data, TempData
from .forms import PhilipsDataForm, SiemensDataForm, GeDataForm, IsmrmrdDataForm, DataForm
from .filters import DataFilter
from .tasks import process_ge_data, process_ismrmrd_data, process_philips_data, process_siemens_data


def data_list(request):
    filter = DataFilter(request.GET, Data.objects.all().order_by('-upload_date'))

    if request.user.is_authenticated:
        temp_datasets = TempData.objects.filter(uploader=request.user).order_by('-upload_date')
    else:
        temp_datasets = []
    
    return render(request, 'mridatabase/data_list.html',
                  {'filter': filter,
                   'temp_datasets': temp_datasets
                  })


def data_description(request, uuid):
    data = get_object_or_404(Data, uuid=uuid)
    scanner = '{} {} T {} scanner'.format(data.scanner_vendor,
                                        data.scanner_field,
                                        data.scanner_model)
    coil = '{}-channel coil array'.format(data.number_of_channels)

    parameters = ''
    
    parameters += 'matrix size of {} x {}'.format(data.matrix_size_x,
                                                  data.matrix_size_y)
    if data.matrix_size_z > 1:
        parameters += ' x {}, '.format(data.matrix_size_z)
    else:
        parameters += ', '
    
    parameters += 'spatial resolution of {} mm x {} mm'.format(data.resolution_x,
                                                               data.resolution_y)
    if data.matrix_size_z > 1:
        parameters += ' x {} mm, '.format(data.resolution_z)
    else:
        parameters += ', '
        
    parameters += 'flip angle of {} degree, '.format(data.flip_angle)
    parameters += 'and TE/TR of {}ms/{}ms.'.format(data.te, data.tr)

    url = request.build_absolute_uri(reverse('data', args=(uuid, )))

    description = 'The data was acquired on a {scanner}, with a {coil}. ' \
                  'Scan parameters include {parameters} ' \
                  'The data can be downloaded from {url}.'.format(scanner=scanner,
                                                                  coil=coil,
                                                                  parameters=parameters,
                                                                  url=url)
    
    return HttpResponse(description, content_type='text/plain')


def data(request, uuid):
    return render(request, 'mridatabase/data.html',
                  {'data': get_object_or_404(Data, uuid=uuid)})


@login_required
def upload_ismrmrd(request):
    IsmrmrdFormSet = formset_factory(IsmrmrdDataForm)
    if request.method == "POST":
        forms = IsmrmrdFormSet(request.POST, request.FILES)
        if forms.is_valid():
            for form in forms:
                ismrmrd_data = form.save(commit=False)
                ismrmrd_data.upload_date = timezone.now()
                ismrmrd_data.uploader = request.user
                ismrmrd_data.save()
                process_ismrmrd_data.delay(ismrmrd_data.uuid)
            return redirect('data_list')
    return render(request, 'mridatabase/upload.html', {'forms': IsmrmrdFormSet})


@login_required
def upload_ge(request):
    GeFormSet = formset_factory(GeDataForm)
    if request.method == "POST":
        forms = GeFormSet(request.POST, request.FILES)
        if forms.is_valid():
            for form in forms:
                ge_data = form.save(commit=False)
                ge_data.upload_date = timezone.now()
                ge_data.uploader = request.user
                ge_data.save()
                process_ge_data.delay(ge_data.uuid)
            return redirect('data_list')
    return render(request, 'mridatabase/upload.html', {'forms': GeFormSet})


@login_required
def upload_philips(request):
    PhilipsFormSet = formset_factory(PhilipsDataForm)
    if request.method == "POST":
        forms = PhilipsFormSet(request.POST, request.FILES)
        if forms.is_valid():
            for form in forms:
                philips_data = form.save(commit=False)
                philips_data.upload_date = timezone.now()
                philips_data.uploader = request.user
                philips_data.save()
                process_philips_data.delay(philips_data.uuid)
            return redirect('data_list')
    return render(request, 'mridatabase/upload.html', {'forms': PhilipsFormSet})

@login_required
def upload_siemens(request):
    SiemensFormSet = formset_factory(SiemensDataForm)
    if request.method == "POST":

        forms = SiemensFormSet(request.POST, request.FILES)
        if forms.is_valid():
            for form in forms:
                siemens_data = form.save(commit=False)
                siemens_data.upload_date = timezone.now()
                siemens_data.uploader = request.user
                siemens_data.save()
                process_siemens_data.delay(siemens_data.uuid)
            return redirect('data_list')
    return render(request, 'mridatabase/upload.html', {'forms': SiemensFormSet})

@login_required
def data_delete(request, uuid):
    data = get_object_or_404(Data, uuid=uuid)
    if request.user == data.uploader:
        data.ismrmrd_file.delete()
        data.thumbnail_file.delete()
        data.delete()
    return redirect("data_list")

@login_required
def temp_data_delete(request, uuid):
    temp_data = get_object_or_404(TempData, uuid=uuid)
    
    if request.user == temp_data.uploader:
        try:
            temp_data.siemens_dat_file.delete()
        except:
            pass
        try:
            temp_data.ge_pfile.delete()
        except:
            pass
        try:
            temp_data.philips_lab_file.delete()
            temp_data.philips_sin_file.delete()
            temp_data.philips_raw_file.delete()
        except:
            pass
        try:
            temp_data.ismrmrd_file.delete()
        except:
            pass
            
        temp_data.delete()
    return redirect("data_list")

@login_required
def data_update_form(request, uuid):
    if request.method == "POST":
        data = get_object_or_404(Data, uuid=uuid)
        form = DataForm(request.POST or None, request.FILES or None, instance=data)
        if form.is_valid():
            form.save()
            return redirect("user_data_list")
    else:
        data = get_object_or_404(Data, uuid=uuid)
        form = DataForm(instance=data)
        return render(request, 'mridatabase/edit_data.html', {'data': data, 'form': form})

@login_required
def user_data_list(request):
    filter = DataFilter(request.GET, Data.objects.filter(uploader=request.user).order_by('-upload_date'))
    
    return render(request, 'mridatabase/my_data_sets.html',
                  {'filter': filter})

def about(request):
    return render(request, 'mridatabase/about.html')


def info(request):
    return render(request, 'mridatabase/info.html')
