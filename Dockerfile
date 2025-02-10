FROM python:3.9-slim

WORKDIR /app

# Gerekli araçları kur
RUN apt-get update && apt-get install -y wget unzip

# Stockfish kurulumu
RUN wget https://stockfishchess.org/files/stockfish-16-linux.zip \
    && unzip stockfish-16-linux.zip \
    && mv stockfish/stockfish-ubuntu-x86-64 stockfish.exe \
    && chmod +x stockfish.exe \
    && rm -rf stockfish-16-linux.zip stockfish

# Model dosyalarını indir
RUN mkdir -p nn && cd nn \
    && wget https://github.com/linrock/chessboard-recognizer/releases/download/v0.5/nn.zip \
    && unzip nn.zip \
    && rm nn.zip

# Python bağımlılıklarını kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodlarını kopyala
COPY *.py ./

# Çalıştır
CMD ["python", "telegram_bot.py"] 