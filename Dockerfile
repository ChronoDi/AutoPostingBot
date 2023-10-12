FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN alembic upgrade head
RUN pip install taskiq

CMD ["python", "app.py"]