import logging
import os
import numpy as np
import boto3
import zipfile
import requests
from io import BytesIO
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from celery.result import AsyncResult
from django.contrib.auth.models import User



from .models import Data, TempData, Uploader, Project, Log
from .forms import PhilipsDataForm, SiemensDataForm, GeDataForm, IsmrmrdDataForm, DataForm
from .filters import DataFilter
from .tasks import process_ge_data, process_ismrmrd_data, process_philips_data, process_siemens_data, download_zip
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


def data_list(request):
    if (request.GET.get("tags")):
        tag = request.GET.get("tags")
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

def data_share(request, uuid):
    # TODO: Add popup of form.
    return data_list(request)

def data(request, uuid):
    logging.warning('Watch out!')  # will print a message to the console
    logging.info('I told you so')  # will not print anything
    logging.warning("UUIDS: {0}".format(uuid))

    if request.user.is_authenticated:

        uuid = uuid.strip("<QuerySet [")
        uuid = uuid.strip('>]>')
        uuid = uuid.strip("Data: ")
        logging.warning(uuid) ## # DEBUG: this is for me to make sure what is in uuid.
        uuids = uuid.split(">, <Data: ")
        for id in uuids:
            id.strip()
        logging.warning("THE UUIDS: ")
        logging.warning(uuids) ## # DEBUG: this is for me to make sure what is in uuid.
        logging.warning("THE TYPE OF UUIDS: {}".format(type(uuids)))
        # download_zip.delay(uuids=uuids)
        # s = download_zip.apply_async(args=[uuids])

        # task = download_zip.delay(uuids)
        # # return redirect('data_list')
        # return render(request, "mridata/poll_for_download.html",
                              # {'task_id': task.task_id})

        # Folder name in ZIP archive which contains the above files
        # E.g [thearchive.zip]/Mri\ Datasets/file.whatever
        s = BytesIO()
        zip_subdir = "Mri Datasets"
        zip_filename = "%s.zip" % zip_subdir
        zf = zipfile.ZipFile(s, 'w')

        # TODO: figure out how to make this in the background.

        for id in uuids:
            data = get_object_or_404(Data, uuid=id)
            data.downloads += 1
            data.save()
            logging.warning("uuid {0}".format(data.ismrmrd_file.url)) # this gives me the files I.e. /media/c0fe34bd-bc71-4e14-a9c2-9e47767a4335.h5
            fdir, fname = os.path.split(data.ismrmrd_file.url)
            zip_path = os.path.join(zip_subdir, fname)

            if settings.USE_AWS:
                data_bytes = requests.get(data.ismrmrd_file.url).content                
                zf.writestr(fname, data_bytes, zip_path)
            else:
                zf.write(data.ismrmrd_file.url, zip_path)

        zf.close()

        resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
        # ..and correct content-disposition
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp
        # return redirect('data_list')
    else:
        return render(request, 'mridata/data.html',
                  {'data': get_object_or_404(Data, uuid=uuid)})

def poll_for_download(request):
    task_id = request.GET.get("task_id")
    filename = request.GET.get("filename")

    if request.is_ajax():
        result = generate_file.AsyncResult(task_id)
        if result.ready():
            return HttpResponse(json.dumps({"filename": result.get()}))
        return HttpResponse(json.dumps({"filename": None}))

    try:
        f = open("/path/to/export/"+filename)
    except:
        return HttpResponseForbidden()
    else:
        response = HttpResponse(file, mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response


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
    # add tags.
    # logging.warning("I AM IN TAGS")
    # logging.warning("request:", request)
    if request.GET:
        # logging.warning("GET REQUEST")
        # logging.warning("tag: {}".format( request.GET.get("tag")))
        # logging.warning("UUID: {}".format(request.GET.get("uuid")))
        uuid = request.GET.get("uuid")
        tagRaw = request.GET.get("tag")

        # logging.warning("\n\n\n GETTING DATA")
        data = get_object_or_404(Data, uuid=uuid)
        # logging.warning("\n\n\n GOT DATA")
        # logging.warning("TAG RAW: ", tagRaw)
        # logging.warning("TAG RAW TYPE: {}".format(type(tagRaw)))
        #
        # logging.warning("TAGS: {}".format(data.tags.all()))

        data.tags.add(tagRaw)
        # logging.warning("\n\n\n GOT tags")
        # logging.warning("TAGS: {}".format(data.tags.all()))

        data.save()
    return redirect("data_list")
    # if request.is_ajax() and request.POST:
    #     tagRaw = request.POST.get('new_tag')
    #     # uuid = request.POST.get('post_uuid');
    #     # data = get_object_or_404(Data, uuid=uuid) # Data Object
    #     # data.tags.add(tagRaw)
    #     logging.warning("Request: {}".format(request.POST))
    #     logging.warning(tagRaw)
    #
    #     return JsonResponse({"tags": dataRaw})
    # return JsonResponse({'tags' : request.GET})


def tag_delete(request, uuid, tag):
    logging.warning("request:", request)
    logging.warning("uuid", uuid)
    logging.warning("tag", tag)
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
