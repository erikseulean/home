FROM python:3.10.1
ADD . /python-flask
WORKDIR /python-flask
RUN python -m pip install -r requirements.txt
EXPOSE 57633