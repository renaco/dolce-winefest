FROM debian:stretch
COPY ./code/requirements.txt /usr/src/app/
WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install -y eatmydata
RUN eatmydata apt-get install -y \
    python-dev \
    default-libmysqlclient-dev \
    python-pip \
    procps
RUN rm -rf /var/lib/apt/lists/*

# install python packages
RUN pip install --upgrade pip
RUN pip install --upgrade \
    setuptools \
    requests \
    mysql-python \
    psiturk

# RUN pip install --upgrade setuptools \
#     && pip install mysql-connector-python

RUN pip install --no-cache-dir -r ./requirements.txt

EXPOSE 5000

CMD ["python", "./app.py"]
