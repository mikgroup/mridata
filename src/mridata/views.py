import os
import numpy as np

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from celery.result import AsyncResult

from .models import Data, TempData, Uploader
from .forms import PhilipsDataForm, SiemensDataForm, GeDataForm, IsmrmrdDataForm, DataForm
from .filters import DataFilter
from .tasks import process_ge_data, process_ismrmrd_data, process_philips_data, process_siemens_data

def about(request):
    return render(request, 'mridata/about.html')


def faq(request):
    return render(request, 'mridata/faq.html')


def data_list(request):
    filter = DataFilter(request.GET, Data.objects.all().order_by('-upload_date'))

    if request.user.is_authenticated:
        uploader = request.user.uploader
        temp_datasets = TempData.objects.filter(uploader=uploader).order_by('-upload_date')
    else:
        temp_datasets = []
    
    return render(request, 'mridata/data_list.html',
                  {'filter': filter,
                   'temp_datasets': temp_datasets
                  })


def data_download(request, uuid):
    data = get_object_or_404(Data, uuid=uuid)
    data.downloads += 1
    data.save()

    return redirect(data.ismrmrd_file.url)


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
                ismrmrd_data.uploader = request.user.uploader
                ismrmrd_data.save()
                process_ismrmrd_data.apply_async(args=[ismrmrd_data.uuid],
                                                 task_id=str(ismrmrd_data.uuid))
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
                ge_data.uploader = request.user.uploader
                ge_data.save()
                process_ge_data.apply_async(args=[ge_data.uuid],
                                            task_id=str(ge_data.uuid))
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
                philips_data.uploader = request.user.uploader
                philips_data.save()
                process_philips_data.apply_async(args=[philips_data.uuid],
                                                 task_id=str(philips_data.uuid))
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
                siemens_data.uploader = request.user.uploader
                siemens_data.save()
                process_siemens_data.apply_async(args=[siemens_data.uuid],
                                                 task_id=str(siemens_data.uuid))
            else:
                return render(request, 'mridata/upload.html', {'form': SiemensDataForm})
            
        return redirect('data_list')
    
    return render(request, 'mridata/upload.html', {'form': SiemensDataForm})

    
@login_required
def data_edit(request, uuid):
    data = get_object_or_404(Data, uuid=uuid)
    if request.user == data.uploader.user:
        if request.method == "POST":
            form = DataForm(request.POST or None, request.FILES or None, instance=data)
            if form.is_valid():
                form.save()
                return redirect("data_list")
        else:
            data = get_object_or_404(Data, uuid=uuid)
            form = DataForm(instance=data)
            return render(request, 'mridata/data_edit.html', {'data': data, 'form': form})


@login_required
def data_delete(request, uuid):
    data = get_object_or_404(Data, uuid=uuid)
    if request.user == data.uploader.user:
        data.ismrmrd_file.delete()
        data.thumbnail_file.delete()
        data.delete()
    return redirect("data_list")


@login_required
def temp_data_delete(request, uuid):
    temp_data = get_object_or_404(TempData, uuid=uuid)
    
    if request.user == temp_data.uploader.user:
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
def check_refresh(request):

    if request.user.is_authenticated:

        uploader = request.user.uploader
        if uploader.refresh:
            uploader.refresh = False
            uploader.save()
            return JsonResponse({'refresh' : True})
            
    return JsonResponse({'refresh' : False})
