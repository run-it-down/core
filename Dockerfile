FROM alpine:3.12.0

RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add python3
RUN apk add --update py-pip
RUN pip install --upgrade pip

ADD core /core/
ADD common /common/
COPY requirements.txt .

RUN pip install -r requirements.txt

ARG RIOT_API_TOKEN
ENV RIOT_API_TOKEN=$RIOT_API_TOKEN

ENV PYTHONPATH "/core/:/common/common/"
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8004", "core.api", "--timeout", "600"]
