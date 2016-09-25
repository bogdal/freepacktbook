FROM python:3.5
ENV PYTHONUNBUFFERED 1

RUN \
 apt-get -y update && \
 apt-get install -y cron && \
 apt-get clean

RUN \
  echo "Europe/Warsaw" > /etc/timezone && \
  dpkg-reconfigure -f noninteractive tzdata

ADD setup.py /app/
RUN cd /app && python setup.py develop

ADD . /app
WORKDIR /app

RUN echo "0 8 * * * /usr/local/bin/claim_free_ebook >> /var/log/cron.log 2>&1" >> /cron-task
RUN touch /var/log/cron.log

CMD \
  env | grep 'PACKT\|SLACK' >> /etc/environment && \
  crontab /cron-task && cron && \
  tail -f /var/log/cron.log
