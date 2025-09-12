# ---------- Build Stage ----------
FROM python:3.12-slim AS builder

# System dependencies für Builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Nur requirements kopieren -> besserer Caching-Effekt
COPY requirements.txt .

# Dependencies ins separaten Ordner installieren
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- Final Stage ----------
FROM python:3.12-slim

# Non-root user anlegen
RUN useradd -m appuser

WORKDIR /app

# Nur installierte Dependencies übernehmen
COPY --from=builder /install /usr/local

# App Code kopieren
COPY src/ .

# Rechte setzen
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5001
# Default Command
CMD ["python", "main.py"]
