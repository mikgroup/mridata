# mridata

This repo contains the source code building the mridata.org website. The only codes that are not public are GE Orchestra code, and AWS related code.

A local server can be set up using Docker, to test and extend features.

## Setting up Docker

Install Docker Community Edition for your platform:

	https://docs.docker.com/engine/installation/

Install docker-compose for your platform:

	https://docs.docker.com/compose/install/#install-compose

## Build and run using docker-compose

Clone the repo, go to that directory and run:

	docker-compose build
	docker-compose up
	
The first time would take a long time to build.
The website can be accessed at http://127.0.0.1:8000

## Web architecture locally

Django is used for web framework and development. 

PostgresSQL is used for database, storing user and data information. 

Celery is used for distributed task queueing, including for ISMRMRD conversion, parameter extraction, and thumbnail generation. 

Redis is used as a message worker for Django, and Celery.

Each of these packages (Django, PostgresSQL, Celery, and Redis) runs in their own Docker images (web, postgres, worker, redis). 

## Code structure

The [src] folder contains the Django source code for the website. [src/mridata_org] contains the project code, and [src/mridata] contains code for the Django app (mridata). [src/templates] contains the HTML template code for each webpage.

### mridata

Data models, which include scan parameters and links to thumbnails and data files, are described in [src/mridata/models.py]. There are two main types of models: Data and TempData. Data is the final model for the stored ISMRMRD data. It must have the thumbnail file, and ismrmrd file populated. TempData has four sub-classes: GeData, SiemensData, PhilipsData, and IsmrmrdData.

Backend processing tasks, including ISMRMRD conversion, and thumbnail extraction, are described in [src/mridata/tasks.py].

Filter options on the main page are described in [src/mridata/filters.py]

Uploading form options are described in [src/mridata/forms.py]
