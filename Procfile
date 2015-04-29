web: honcho start --procfile HerokuProcfile
web_only: gunicorn mozy.wsgi -c mozy/gunicorn.conf -w 3
worker: django-admin.py run_huey
worker_only: django-admin.py run_huey --no-periodic
