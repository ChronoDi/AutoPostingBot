FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN alembic -с /app/alembic.ini upgrade head

COPY . .

CMD ["python", "your_script.py"]