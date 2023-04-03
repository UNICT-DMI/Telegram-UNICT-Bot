FROM python:3.9.12-slim
WORKDIR /unictbot

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT [ "python3", "main.py" ]
