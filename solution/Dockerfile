FROM python:3.12.1-alpine3.19

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .



CMD ["python", "main.py"]
