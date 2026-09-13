FROM python:3.12-slim AS base

WORKDIR /src

COPY requirements/ ./requirements

ARG REQUIREMENTS=base

RUN pip install --upgrade pip && \
    pip install -r requirements/${REQUIREMENTS}.txt

COPY . .

ENV PYTHONPATH=/src

EXPOSE 8081

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8081"]
