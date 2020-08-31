FROM tiangolo/uwsgi-nginx-flask:python3.8

RUN apk --update add bash nano
RUN pip install pip==20.2.2

ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static

COPY ./requirements.txt /var/www/requirements.txt

RUN pip install -r /var/www/requirements.txt