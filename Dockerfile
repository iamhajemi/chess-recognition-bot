FROM python:3.9-slim

WORKDIR /app

# Gerekli araçları kur
RUN apt-get update && apt-get install -y wget unzip

# Model dosyalarını indir
RUN mkdir -p nn && cd nn \
    && wget https://github.com/linrock/chessboard-recognizer/releases/download/v0.5/nn.zip \
    && unzip nn.zip \
    && rm nn.zip

# Python bağımlılıklarını kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodlarını ve stockfish'i kopyala
COPY *.py ./
COPY stockfish.exe ./
RUN chmod +x stockfish.exe

# Çalıştır
CMD ["python", "telegram_bot.py"] 