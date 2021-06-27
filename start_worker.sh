cd src
celery -A mridata_org worker -l info --concurrency=1
