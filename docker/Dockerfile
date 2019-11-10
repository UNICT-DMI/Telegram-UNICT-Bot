FROM alpine:latest

ARG UNICTBOT_REPO="https://github.com/UNICT-DMI/Telegram-UNICT-Bot.git"
ENV UNICTBOT_DIR="/unictbot"

RUN apk update &&\
    apk --no-cache add py-pip git bash libressl-dev postgresql-dev libffi-dev gcc musl-dev python3-dev

RUN pip3 install --upgrade pip &&\
    pip3 install requests beautifulsoup4 pyyaml python-telegram-bot

RUN mkdir -p "$UNICTBOT_DIR" &&\ 
    git clone "$UNICTBOT_REPO" "$UNICTBOT_DIR" &&\
    mkdir -p "$UNICTBOT_DIR"/logs &&\
    touch "$UNICTBOT_DIR"/logs.txt &&\
    touch "$UNICTBOT_DIR"/errors.txt

COPY settings.yaml "$UNICTBOT_DIR"/config/settings.yaml
COPY entrypoint.sh /

ENTRYPOINT [ "/entrypoint.sh"]