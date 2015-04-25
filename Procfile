web: gunicorn mozy.wsgi -c mozy/gunicorn.conf -w 3
worker: django-admin.py run_huey --no-periodic
scheduler: django-admin.py run_huey --periodic
