FROM nginx:1.25
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

# pull base image
FROM python:3.12.5

# set working directory
WORKDIR /usr/src/app

# Prevent python from writing pyc files
# and from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"

# install dependencies
RUN pip install --upgrade pip
RUN pip install unidecode
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
