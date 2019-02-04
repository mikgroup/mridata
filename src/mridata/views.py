import logging
import os
import numpy as np
import boto3
import zipfile
from io import BytesIO
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from celery.result import AsyncResult
from django.contrib.auth.models import User
from django.db.models import Q



from .models import Data, TempData, Uploader, Project, Log
from .forms import PhilipsDataForm, SiemensDataForm, GeDataForm, IsmrmrdDataForm, DataForm
from .filters import DataFilter
from .tasks import process_ge_data, process_ismrmrd_data, process_philips_data, process_siemens_data
from taggit.models import Tag

def main(request):
    projects = Project.objects.all().order_by('-name')
    return render(request, 'mridata/main.html', {'projects': projects})


def about(request):
    return render(request, 'mridata/about.html')


def faq(request):
    return render(request, 'mridata/faq.html')


def terms(request):
    return render(request, 'mridata/terms.html')


def api(request):
    return render(request, 'mridata/api.html')


def get_option(opt, options):
    actual = ('tag', 'system_vendor', 'system_model','protocol_name',
    'sequence_type','sequence_type', 'coil_name', 'uuid', 'fullysampled',
    'references')
    abrev = ('tags', 'vendor', 'model', 'protocol', 'type','sequence',
    'coil', 'id', 'sampled', 'ref')

    if opt not in abrev and opt in options:
        return opt

    for i in range(len(abrev)):
        if opt == abrev[i]:
            return actual[i]
    return 'other'



def get_value(val, uploader):
    if val == "me":
        return uploader
    elif val in ('yes', 'y', 't', 'true', '1'):
        return 1
    elif val in ('no', 'n', 'f', 'false', '0'):
        return 0
    elif val == "unknown":
        return ''
    elif 'and' in val:
        return val.replace('and', ',')
    else:
        return val

def search(result, request):
    get = request.GET
    if not result:
        return get
    else:
        result = result.lower()
    options = ('uploader', 'tag', 'project', 'anatomy',
    'references', 'comments', 'tags', 'funding_support',
    'system_vendor', 'vendor', 'model', 'protocol', 'type',
    'coil', 'sequence', 'system_model', 'protocol_name',
    'coil_name', 'sequence_type', 'uuid', 'id', 'sampled',
    'fullysampled', 'ref') # for each model, coil, sequence....

    results = result.split(',')
    for res in results:
        r = res.split(':')
        # Need the try catch in case r[0]/r[1] fails.
        try:
            option = get_option(r[0].strip(), options)
            if option == 'other':
                value = r
            else:
                value = get_value(r[1].strip(), request.user.uploader)
            if option in options:
                get[option] = value
            else:
                get['other'] = r
        except Exception:
            get['csrfmiddlewaretoken'] += str(r)

    if 'csrfmiddlewaretoken' in get:
        get.pop('csrfmiddlewaretoken')
    # if no ',' then contains in each and combine.
    # if there is ',' and ':' then put in appropriate category.
    return get


def data_list(request):
    result = request.GET.get('search')
    request.GET = request.GET.copy()
    request.GET['search'] = ''
    request.GET = search(result, request)
    if (request.GET.get('other')):
        options = request.GET.get('other')
        filter = Data.objects.filter(Q(tags__name__in=options) | Q(anatomy__icontains=options[0]) |
                                Q(references__icontains=options[0]) | Q(comments__icontains=options[0]) |
                                Q(funding_support__icontains=options[0]) | Q(protocol_name__icontains=options[0]) |
                                Q(series_description__icontains=options[0]) | Q(system_vendor__icontains=options[0]) |
                                Q(system_model__icontains=options[0]) | Q(coil_name__icontains=options[0]) |
                                Q(institution_name__icontains=options[0]) | Q(uploader__user__username= options[0]) |
                                Q(project__name__icontains=options[0])).distinct()
        request.GET['other'] = ''
        filter = DataFilter(request.GET, filter.order_by('-upload_date'))
    elif (request.GET.get("tag")):
        tag = request.GET.get("tag")
        tag = tag.split()
        tag_filter = Data.objects.filter(tags__name__in=tag).distinct()

        request.GET = request.GET.copy() # makes request mutable.
        request.GET['tags'] = "" # deletes all tags so you can filter everything else.
        filter = DataFilter(request.GET, tag_filter.order_by("-upload_date"))

    else:
        filter = DataFilter(request.GET, Data.objects.all().order_by('-upload_date'))

    if request.user.is_authenticated:
        uploader = request.user.uploader
        temp_datasets = TempData.objects.filter(uploader=uploader).order_by('-upload_date')
        logs = Log.objects.filter(user=request.user).order_by('-date_time')
    else:
        temp_datasets = []
        logs = []

    if request.is_ajax() and 'page' in request.GET:
        template = 'mridata/data_list_page.html'
    else:
        template = 'mridata/data_list.html'

    return render(request, template,
                  {
                      'filter': filter,
                      'temp_datasets': temp_datasets,
                      'logs': logs
                  })


def data_download(request, uuid):
    data = get_object_or_404(Data, uuid=uuid)
    data.downloads += 1
    data.save()
    return redirect(data.ismrmrd_file.url)


@login_required
def upload_ismrmrd(request):
    if request.method == "POST":
        form = IsmrmrdDataForm(request.POST, request.FILES)
        if form.is_valid():
            project, created = Project.objects.get_or_create(
                name=form.cleaned_data['project_name'],
            )
            ismrmrd_data = form.save(commit=False)
            ismrmrd_data.project = project
            ismrmrd_data.upload_date = timezone.now()
            ismrmrd_data.uploader = request.user.uploader
            ismrmrd_data.save()
            # form.save_m2m()

            log = Log(string="{} uploaded. Waiting for backend processing.".format(
                str(ismrmrd_data)[37:]), user=request.user)
            log.save()

            request.user.uploader.refresh = True
            request.user.uploader.save()
            process_ismrmrd_data.apply_async(args=[ismrmrd_data.uuid],
                                             task_id=str(ismrmrd_data.uuid))
        else:
            return render(request, 'mridata/upload.html', {'form': IsmrmrdDataForm})

        return redirect('data_list')

    return render(request, 'mridata/upload.html', {'form': IsmrmrdDataForm})


@login_required
def upload_ge(request):
    if request.method == "POST":
        form = GeDataForm(request.POST, request.FILES)
        if form.is_valid():
            project, created = Project.objects.get_or_create(
                name=form.cleaned_data['project_name'],
            )
            ge_data = form.save(commit=False)
            ge_data.project = project
            ge_data.upload_date = timezone.now()
            ge_data.uploader = request.user.uploader
            ge_data.save()

            log = Log(string="{} uploaded. Waiting for backend processing.".format(
                str(ge_data)[37:]), user=request.user)
            log.save()

            request.user.uploader.refresh = True
            request.user.uploader.save()
            process_ge_data.apply_async(args=[ge_data.uuid],
                                        task_id=str(ge_data.uuid))
        else:
            return render(request, 'mridata/upload.html', {'form': GeDataForm})

        return redirect('data_list')

    return render(request, 'mridata/upload.html', {'form': GeDataForm})


@login_required
def upload_philips(request):
    if request.method == "POST":
        form = PhilipsDataForm(request.POST, request.FILES)
        if form.is_valid():
            project, created = Project.objects.get_or_create(
                name=form.cleaned_data['project_name'],
            )
            philips_data = form.save(commit=False)
            philips_data.project = project
            philips_data.upload_date = timezone.now()
            philips_data.uploader = request.user.uploader

            philips_data.save()

            log = Log(string="{} uploaded. Waiting for backend processing.".format(
                str(philips_data)[37:]), user=request.user)

            log.save()

            request.user.uploader.refresh = True
            request.user.uploader.save()
            process_philips_data.apply_async(args=[philips_data.uuid],
                                             task_id=str(philips_data.uuid))
        else:
            return render(request, 'mridata/upload.html', {'form': PhilipsDataForm})

        return redirect('data_list')
    return render(request, 'mridata/upload.html', {'form': PhilipsDataForm})

@login_required
def upload_siemens(request):
    if request.method == "POST":
        form = SiemensDataForm(request.POST, request.FILES)
        if form.is_valid():
            project, created = Project.objects.get_or_create(
                name=form.cleaned_data['project_name'],
            )
            siemens_data = form.save(commit=False)
            siemens_data.project = project
            siemens_data.upload_date = timezone.now()
            siemens_data.uploader = request.user.uploader
            siemens_data.save()

            log = Log(string="{} uploaded. Waiting for backend processing.".format(
                str(siemens_data)[37:]), user=request.user)
            log.save()

            request.user.uploader.refresh = True
            request.user.uploader.save()
            process_siemens_data.apply_async(args=[siemens_data.uuid],
                                             task_id=str(siemens_data.uuid))
        else:
            return render(request, 'mridata/upload.html', {'form': SiemensDataForm})

        return redirect("data_list")

    return render(request, 'mridata/upload.html', {'form': SiemensDataForm})


@login_required
def data_edit(request, uuid):
    data = get_object_or_404(Data, uuid=uuid)
    if request.user == data.uploader.user:
        if request.method == "POST":
            form = DataForm(request.POST or None, request.FILES or None, instance=data)
            if form.is_valid():
                project, created = Project.objects.get_or_create(
                    name=form.cleaned_data['project_name'],
                )
                data = form.save(commit=False)
                data.project = project
                data.save()

                return redirect("data_list")
        else:
            data = get_object_or_404(Data, uuid=uuid)

            form = DataForm(instance=data, initial={'project_name': data.project.name})
            return render(request, 'mridata/data_edit.html', {'data': data, 'form': form, 'image_url': data.thumbnail_file.url})


@login_required
def data_delete(request, uuid):
    data = get_object_or_404(Data, uuid=uuid)
    if request.user == data.uploader.user:
        data.ismrmrd_file.delete()
        data.thumbnail_file.delete()
        data.delete()
    return redirect("data_list")


@login_required
def clear_log(request):
    if request.user.is_authenticated:
        for log in Log.objects.filter(user=request.user):
            log.delete()

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

@login_required
def tags(request):
    if request.GET:
        uuid = request.GET.get("uuid")
        tagRaw = request.GET.get("tag")
        if tagRaw == "" or not tagRaw:
            return redirect('data_list')
        data = get_object_or_404(Data, uuid=uuid)
        tags = tagRaw.split(',')
        for tag in tags:
            t = tag.strip()
            logging.warning("ADDING TAG: {}".format(t))
            data.tags.add(t)
            data.save()
    return redirect("data_list")


def search_tag(request, tag):
    tag = [tag]
    logging.warning("tag {}".format(tag))
    logging.warning("request {}".format(request.GET))
    for val in request.GET.values():
        return data_list(request)

    tag_filter = Data.objects.filter(tags__name__in=tag).distinct()

    filter = DataFilter(request.GET, tag_filter.order_by("-upload_date"))

    if request.user.is_authenticated:
        uploader = request.user.uploader
        temp_datasets = TempData.objects.filter(uploader=uploader).order_by('-upload_date')
        logs = Log.objects.filter(user=request.user).order_by('-date_time')
    else:
        temp_datasets = []
        logs = []

    if request.is_ajax() and 'page' in request.GET:
        template = 'mridata/data_list_page.html'
    else:
        template = 'mridata/data_list.html'

    return render(request, template,
                  {
                      'filter': filter,
                      'temp_datasets': temp_datasets,
                      'logs': logs
                  })

def tag_delete(request, uuid, tag):
    logging.warning("IM HERE")
    data = get_object_or_404(Data, uuid=uuid)
    data.tags.remove(tag)
    data.save()
    return redirect('data_list')


@login_required
def get_temp_credentials(request):
    if request.user.is_authenticated:
        client = boto3.client('sts')
        r = client.assume_role(RoleArn='arn:aws:iam::876486404445:role/mridata-assets-s3-uploader',
                               RoleSessionName=str(request.user))
        return JsonResponse(r['Credentials'])
