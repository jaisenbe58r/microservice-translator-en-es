FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7

RUN apk --update add bash nano
RUN apt-get update && \
    apt-get install -y git && \
    apt-get install -y libsm6 libxext6 libxrender-dev && \
    pip install --upgrade pip && \

ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static

COPY ./requirements.txt /var/www/requirements.txt

RUN pip install -r /var/www/requirements.txt