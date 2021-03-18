FROM python:3-slim
WORKDIR /unictbot

COPY requirements.txt .
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "main.py" ]