FROM python:rc-alpine3.10

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD find_store.py .

ENTRYPOINT ["python", "find_store.py"]
