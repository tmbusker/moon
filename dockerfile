# FROM python:3.11-bullseye AS ldap-build

# RUN apt-get update -y && \ 
#     apt-get install -y libsasl2-dev python-dev libldap2-dev libssl-dev && \
#     python -m pip wheel --wheel-dir=/tmp python-ldap==3.4.3

FROM python:3.11-bullseye

RUN apt-get update && apt-get install -y libldap2-dev libsasl2-dev

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /busking
COPY . /busking/
RUN pip install -r requirements.txt

EXPOSE 8000

# Run Django migrations and start the application
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000
