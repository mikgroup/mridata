# mridata

This repo contains the source code building the mridata.org website. The only codes that are not public are the GE Orchestra code, and AWS account related code.

A local server can be set up using Docker, to test and extend features.

## Setting up Docker

Install Docker Community Edition for your platform:

	https://docs.docker.com/engine/installation/

Install docker-compose:

	https://docs.docker.com/compose/install/#install-compose

## Build and run using docker-compose

Clone the repo, go to that directory and run:

	docker-compose build
	docker-compose up

## Web architecture

Django is used for web framework and development. 

PostgresSQL is used for database, storing user and data information. 

Celery is used for distributed task queueing, including for ISMRMRD conversion, parameter extraction, and thumbnail generation. 

Redis is used as a message worker for Django, and Celery.

Each of these packages (Django, PostgresSQL, Celery, and Redis) runs in their own Docker images (web, postgres, worker, redis). 
