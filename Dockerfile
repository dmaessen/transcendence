FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFERED 1

WORKDIR /app

RUN python3 -m pip install --upgrade pip setuptools wheel

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

CMD ["python", "./backend/manage.py", "runserver", "0.0.0.0:8000"]