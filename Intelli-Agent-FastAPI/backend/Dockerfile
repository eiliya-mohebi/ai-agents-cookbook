FROM python:latest

WORKDIR /app

RUN python -m venv /opt/venv/
ENV PATH=/opt/venv/bin:$PATH

COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY ./src .

