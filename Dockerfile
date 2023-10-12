FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN alembic upgrade head

CMD ["python", "your_script.py"]