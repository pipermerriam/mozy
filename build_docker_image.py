import os


def initialize():
    """
    basic setup.
    """
    if not os.path.exists('build'):
        os.mkdir('build')


template = """
FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
RUN apt-get update
RUN apt-get install -y zip
RUN wget https://github.com/pipermerriam/mozy/archive/master.zip
RUN unzip master.zip

ADD mozy /app
ADD setup.py /app/
ADD requirements.txt /app/

RUN pip install -r requirements.txt
RUN python setup.py install

EXPOSE 80

ENTRYPOINT ["gunicorn"]
CMD ["mozy.wsgi","-w","3","-b","0.0.0.0:8000"]

{env}
""".strip()


def main():
    initialize()
    with open('Dockerfile', 'w') as f:
        with open('.env_docker') as env_f:
            contents = template.format(env=env_f.read())
        f.write(contents)


if __name__ == "__main__":
    main()
