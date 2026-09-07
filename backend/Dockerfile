FROM python:3.9-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps \
		build-base \
		libffi-dev \
		openssl-dev \
		cargo \
	&& python -m pip install --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt \
	&& apk del .build-deps

COPY main.py .
COPY app ./app

RUN addgroup -S appgroup \
	&& adduser -S appuser -G appgroup \
	&& chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]