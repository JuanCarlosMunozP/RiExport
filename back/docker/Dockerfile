FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONNUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements/ ./requirements

ARG REQUIREMENTS=base

RUN pip install --upgrade pip && \
    pip install -r requirements/${REQUIREMENTS}.txt

COPY . .

EXPOSE 8081

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8081"]
