FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

COPY . .
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
	&& mkdir -p /app/output /app/logs \
	&& chown -R appuser:appuser /app

USER appuser

CMD ["python", "main.py"]
