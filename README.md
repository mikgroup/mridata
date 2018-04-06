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

## Local web architecture

Django is used for web framework and development. 

PostgresSQL is used for database, storing user and data information. 

Celery is used for distributed task queueing, including for ISMRMRD conversion, parameter extraction, and thumbnail generation. 

Redis is used as a message worker for Django, and Celery.

Each of these packages (Django, PostgresSQL, Celery, and Redis) runs in their own Docker images (web, postgres, worker, redis). 

## Code structure

- [src](src) contains the Django source code for the website. 
..- [src/mridata_org](src/mridata_org) is the project directory, which includes settings for celery, storages, and apps.
..- [src/mridata](src/mridata) contains code for the mridata Django app. This is where most of the code is.
..- [src/templates](src/templates) contains the HTML template code for each webpage.
..- [src/static](src/static) contains logos, javascripts, and css.

### mridata Django app.

- [models.py](src/mridata/models.py) contains two main models. Data, which contains scan parameters and links to thumbnails and the final ISMRMD data file. And TempData, which links to the temporary uploaded data, and has four sub-classes: GeData, SiemensData, PhilipsData, and IsmrmrdData.

- [tasks.py](src/mridata/tasks.py) contains backend processing tasks, including ISMRMRD conversion, and thumbnail extraction. Failure of ISMRMRD conversion traces back to here.

- [views.py](src/mridata/views.py) contains how GET and POST requests are processed for each page.

- [filters.py](src/mridata/filters.py) contains filter options on the main page.

- [forms.py](src/mridata/forms.py) contains upload form options.
