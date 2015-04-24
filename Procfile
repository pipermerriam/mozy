web: gunicorn mozy.wsgi -c mozy/gunicorn.conf -w 3
worker: python manage.py run_huey
