FROM python:3.8
ENV PYTHONUNBUFFERED=1

WORKDIR /home/juanse1080/Deploy

RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc libc-dev python3-dev default-libmysqlclient-dev default-mysql-client

ENV VIRTUAL_ENV=/home/juanse1080/venv
RUN python3 -m venv $VIRTUAL_ENV
RUN echo $VIRTUAL_ENV/bin:$PATH
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY local $VIRTUAL_ENV/lib/python3.8/site-packages