FROM python:3.8.3

ENV APP_HOME /kpi_network
WORKDIR $APP_HOME

COPY . .

RUN apt-get -y update
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install -r requirements.txt