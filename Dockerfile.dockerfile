FROM python:3.6.6-alpine

RUN adduser -D nsync

WORKDIR /home/shookke

RUN apk add --no-cache --virtual .pynacl_deps build-base python3-dev libffi-dev openssl-dev

COPY requirements.txt requirements.txt
RUN python3 -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn
RUN venv/bin/pip install gunicorn pymysql

COPY app app
COPY migrations migrations
COPY devapp.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP devapp.py
# ENV MAIL_SERVER=mail.nsyncdata.net
# ENV MAIL_PORT=587
# ENV MAIL_USE_TLS=1
# ENV MAIL_USERNAME=kevin
# ENV MAIL_PASSWORD=Firefly1

#RUN chown -R shookke:shookke ./
#USER shookke

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]