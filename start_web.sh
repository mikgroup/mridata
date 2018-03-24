cd src
python manage.py makemigrations mridata --noinput
python manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.filter(email='admin@example.com').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'password')" | python manage.py shell
python manage.py runserver 0.0.0.0:8000
