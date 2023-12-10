FROM ubuntu:20.04
WORKDIR /app
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN apt-get install -y  curl apt-transport-https
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update --fix-missing
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools
RUN apt-get install -y unixodbc-dev


RUN apt-get install -y libxml2-dev libxslt1-dev  git locales
RUN apt-get install -y python3.10-dev 
RUN apt install -y python3.10
RUN update-alternatives --install /usr/bin/python python  /usr/bin/python3.10 1
RUN apt install -y python3-distutils
RUN curl https://bootstrap.pypa.io/get-pip.py | python -
RUN pip install --upgrade pip
RUN apt-get install -y --reinstall build-essential
RUN apt install -y python3.11-dev


WORKDIR /code
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .

ENV FLASK_DEBUG=0
EXPOSE 8000

ENTRYPOINT ["gunicorn", "flaskr:create_app(False)"]