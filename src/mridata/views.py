import os
import numpy as np

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse

from .models import Data, TempData
from .forms import PhilipsDataForm, SiemensDataForm, GeDataForm, IsmrmrdDataForm
from .filters import DataFilter
from .tasks import process_ge_data, process_ismrmrd_data, process_philips_data, process_siemens_data


def data_list(request):
    filter = DataFilter(request.GET, Data.objects.all().order_by('-upload_date'))

    if request.user.is_authenticated:
        temp_datasets = TempData.objects.filter(uploader=request.user).order_by('-upload_date')
    else:
        temp_datasets = []
    
    return render(request, 'mridata/data_list.html',
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
    return render(request, 'mridata/data.html',
                  {'data': get_object_or_404(Data, uuid=uuid)})


@login_required
def upload_ismrmrd(request):
    if request.method == "POST":
        for ismrmrd_file in request.FILES.getlist('ismrmrd_file'):
            request.FILES['ismrmrd_file'] = ismrmrd_file
            form = IsmrmrdDataForm(request.POST, request.FILES)
            if form.is_valid():
                ismrmrd_data = form.save(commit=False)
                ismrmrd_data.upload_date = timezone.now()
                ismrmrd_data.uploader = request.user
                ismrmrd_data.save()
                process_ismrmrd_data.delay(ismrmrd_data.uuid)
            else:
                return render(request, 'mridata/upload.html', {'form': IsmrmrdDataForm})               
        return redirect('data_list')
    return render(request, 'mridata/upload.html', {'form': IsmrmrdDataForm})


@login_required
def upload_ge(request):
    if request.method == "POST":
        for ge_pfile in request.FILES.getlist('ge_pfile'):
            request.FILES['ge_pfile'] = ge_pfile
            form = GeDataForm(request.POST, request.FILES)
            if form.is_valid():
                ge_data = form.save(commit=False)
                ge_data.upload_date = timezone.now()
                ge_data.uploader = request.user
                ge_data.save()
                process_ge_data.delay(ge_data.uuid)
            else:
                return render(request, 'mridata/upload.html', {'form': GeDataForm})
        return redirect('data_list')
    return render(request, 'mridata/upload.html', {'form': GeDataForm})


@login_required
def upload_philips(request):
    if request.method == "POST":
        for (philips_lab_file,
             philips_raw_file,
             philips_sin_files) in zip(request.FILES.getlist('philips_lab_file'),
                                       request.FILES.getlist('philips_raw_file'),
                                       request.FILES.getlist('philips_sin_file')):
            
            request.FILES['philips_lab_file'] = philips_lab_file
            request.FILES['philips_raw_file'] = philips_raw_file
            request.FILES['philips_sin_file'] = philips_sin_file
            
            form = PhilipsDataForm(request.POST, request.FILES)
            if form.is_valid():
                philips_data = form.save(commit=False)
                philips_data.upload_date = timezone.now()
                philips_data.uploader = request.user
                philips_data.save()
                process_philips_data.delay(philips_data.uuid)
            else:
                return render(request, 'mridata/upload.html', {'form': PhilipsDataForm})
            
        return redirect('data_list')
    return render(request, 'mridata/upload.html', {'form': PhilipsDataForm})

@login_required
def upload_siemens(request):
    if request.method == "POST":
        for siemens_dat_file in request.FILES.getlist('siemens_dat_file'):
            request.FILES['siemens_dat_file'] = siemens_dat_file
            form = SiemensDataForm(request.POST, request.FILES)
            if form.is_valid():
                siemens_data = form.save(commit=False)
                siemens_data.upload_date = timezone.now()
                siemens_data.uploader = request.user
                siemens_data.save()
                process_siemens_data.delay(siemens_data.uuid)
            else:
                return render(request, 'mridata/upload.html', {'form': SiemensDataForm})
            
        return redirect('data_list')
    return render(request, 'mridata/upload.html', {'form': SiemensDataForm})

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
            return redirect("data_list")
    else:
        data = get_object_or_404(Data, uuid=uuid)
        form = DataForm(instance=data)
        return render(request, 'mridata/edit_data.html', {'data': data, 'form': form})

def about(request):
    return render(request, 'mridata/about.html')


def info(request):
    return render(request, 'mridata/info.html')
