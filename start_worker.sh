cd src
celery worker -l info -A mridata_org --concurrency=1
