FROM python:3.7.7
ENV PYTHONUNBUFFERED 1

ARG build_env
ENV BUILD_ENV ${build_env}

RUN [ -d /splitit ] || mkdir /splitit;
COPY ./splitit /splitit
COPY  requirements.txt /splitit
WORKDIR /splitit
RUN pip install -r requirements.txt