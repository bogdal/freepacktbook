FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1

ARG TZ=Europe/Warsaw
RUN \
  apk --update add tzdata && \
  cp /usr/share/zoneinfo/$TZ /etc/localtime

ADD setup.py /app/
RUN cd /app && python setup.py develop

ADD . /app
WORKDIR /app

RUN echo "0 8 * * * /usr/local/bin/claim_free_ebook" > /var/spool/cron/crontabs/root

ENV PACKTPUB_BOOKS_DIR='/data'
VOLUME ['/data']

CMD crond -f -l 2
