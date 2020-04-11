FROM python:3.7.7-buster

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD find_store.py .

ENTRYPOINT ["python", "find_store.py"]
