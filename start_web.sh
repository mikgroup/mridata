cd src
python manage.py makemigrations mridata --noinput
python manage.py syncdb
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
