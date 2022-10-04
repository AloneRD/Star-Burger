FROM python:buster
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /Star-Burger

COPY requirements.txt /Star-Burger/
RUN pip install -r requirements.txt



COPY . /Star-Burger/
RUN python manage.py collectstatic --noinput