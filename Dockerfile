FROM python:3.11-slim-bullseye

WORKDIR /app

# System-Abhaengigkeiten
RUN apt-get update && apt-get install -y --no-install-recommends \
    pcsc-tools \
    pcscd \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhaengigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App-Code
COPY app/ ./app/

# ERiC SDK Libraries (Linux x86_64)
COPY eric_lib/linux64/*.so /app/eric_lib/
COPY eric_lib/linux64/plugins/*.so /app/eric_lib/plugins/

# Verzeichnisse
RUN mkdir -p /app/certs /app/logs

# ERiC Library-Pfad — BEIDE Verzeichnisse
ENV LD_LIBRARY_PATH="/app/eric_lib:/app/eric_lib/plugins"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
