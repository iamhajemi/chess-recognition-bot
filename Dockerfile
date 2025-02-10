FROM python:3.9-slim

WORKDIR /app

# Gerekli araçları kur
RUN apt-get update && apt-get install -y wget unzip

# Python bağımlılıklarını kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodlarını, stockfish'i ve model dosyalarını kopyala
COPY *.py ./
COPY stockfish ./
COPY nn/ ./nn/
RUN chmod +x stockfish

# Worker ayarları
ENV PYTHONUNBUFFERED=1

# Bellek sınırlamaları
ENV MEMORY_LIMIT=512m
ENV SWAP_LIMIT=1024m

# Port'u aç
EXPOSE 10000

# Çalıştır
CMD ["python", "telegram_bot.py"] 