# pull official base image
FROM python:3.7

ENV PYTHONUNBUFFERED 1

# set working directory
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y curl vim zip unzip python3-dev default-libmysqlclient-dev \
		gcc \
		gettext \
        --no-install-recommends && rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip install --upgrade pip
RUN pip install pipenv
RUN pip install postgres
COPY ./Pipfile /usr/src/app/Pipfile
RUN pipenv install --skip-lock --system --dev

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/


CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

