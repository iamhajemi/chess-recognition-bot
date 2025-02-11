#!/usr/bin/env python3

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from recognize import predict_chessboard, load_model_if_needed
import tempfile
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import nest_asyncio
import requests
import asyncio

# Event loop düzeltmesi
nest_asyncio.apply()

# Loglama ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot token'ı environment variable'dan al
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set!")

# Service URL'ini environment variable'dan al veya default değer kullan
SERVICE_URL = os.environ.get("RENDER_EXTERNAL_URL")

# Web sunucusu için basit handler
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        response = f"""
        <html>
            <head><title>Satranç Tahtası Tanıma Botu</title></head>
            <body>
                <h1>Satranç Tahtası Tanıma Botu Aktif</h1>
                <p>Bot başarıyla çalışıyor. Telegram'dan @ChessRecognitionBot ile iletişime geçebilirsiniz.</p>
                <p>Son kontrol zamanı: {current_time}</p>
            </body>
        </html>
        """
        self.wfile.write(response.encode('utf-8'))

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

def start_web_server():
    """Web sunucusunu başlat"""
    port = int(os.environ.get("PORT", 10000))
    print(f"Web sunucusu {port} portunda başlatılıyor...")
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Web sunucusu başlatıldı ve {port} portunu dinliyor")
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot başlatıldığında çalışacak komut"""
    # Model'i başlangıçta yükle
    load_model_if_needed()
    await update.message.reply_text(
        'Merhaba! Ben bir satranç tahtası tanıma botuyum. '
        'Bana bir satranç tahtası fotoğrafı gönder, ben sana:\n\n'
        '1. FEN notasyonunu\n'
        '2. Lichess analiz linkini göndereceğim.\n\n'
        'İyi oyunlar! 🎮'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yardım komutu"""
    await update.message.reply_text(
        'Kullanım:\n'
        '1. Bana bir satranç tahtası fotoğrafı gönder\n'
        '2. Ben sana FEN notasyonunu ve en iyi hamleyi göstereceğim\n'
        '3. /start - Botu başlat\n'
        '4. /help - Bu yardım mesajını göster'
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fotoğraf geldiğinde çalışacak fonksiyon"""
    temp_file = None
    processing_msg = None
    try:
        # Model'i yükle
        load_model_if_needed()
        
        # Kullanıcıya işlemin başladığını bildir
        processing_msg = await update.message.reply_text("Fotoğraf işleniyor...")

        # Fotoğrafı al (en büyük boyuttaki versiyonu)
        photo = await update.message.photo[-1].get_file()
        
        # Benzersiz bir geçici dosya adı oluştur
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'_{int(time.time())}.png').name
        
        # Fotoğrafı geçici dosyaya kaydet
        await photo.download_to_drive(temp_file)
        
        try:
            # Satranç tahtasını analiz et
            fen, confidence = predict_chessboard(temp_file, type('Args', (), {'quiet': True, 'debug': False})())
            
            # Güvenilirlik yüzdesini hesapla
            confidence_percentage = confidence * 100
            
            # Güvenilirlik emojisi seç
            if confidence_percentage >= 95:
                emoji = "🟢"  # Yüksek güvenilirlik
            elif confidence_percentage >= 85:
                emoji = "🟡"  # Orta güvenilirlik
            else:
                emoji = "🔴"  # Düşük güvenilirlik
            
            # FEN notasyonunu ve güvenilirliği gönder
            await update.message.reply_text(
                f"FEN Notasyonu:\n`{fen}`\n\n"
                f"Tahmin güvenilirliği: {emoji} %{confidence_percentage:.1f}",
                parse_mode='Markdown'
            )
            
            # Lichess analiz linki
            lichess_url = f"https://lichess.org/analysis/standard/{fen}"
            await update.message.reply_text(f"Lichess'te analiz et:\n{lichess_url}")
            
            # Düşük güvenilirlik uyarısı
            if confidence_percentage < 85:
                await update.message.reply_text(
                    "⚠️ Uyarı: Tahmin güvenilirliği düşük. Lütfen FEN notasyonunu kontrol edin. "
                    "Daha iyi sonuç için:\n"
                    "1. Tahtanın tamamı fotoğraf karesinde olmalı\n"
                    "2. Fotoğraf net ve iyi aydınlatılmış olmalı\n"
                    "3. Taşlar net görünmeli"
                )
            
        except Exception as e:
            await update.message.reply_text(f"Satranç tahtası analiz edilirken bir hata oluştu: {str(e)}")
        
    except Exception as e:
        await update.message.reply_text(f"Bir hata oluştu: {str(e)}")
    
    finally:
        # Geçici dosyayı temizle
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except:
                pass
        
        # İşlem mesajını temizle
        if processing_msg:
            try:
                await processing_msg.delete()
            except:
                pass

def keep_alive():
    """Servisi canlı tutmak için periyodik olarak ping at"""
    while True:
        try:
            if SERVICE_URL:
                response = requests.get(SERVICE_URL)
                print(f"Self-ping status: {response.status_code}")
            time.sleep(840)  # 14 dakika (Render'ın 15 dakika sleep limitinden önce)
        except Exception as e:
            print(f"Self-ping error: {str(e)}")
            time.sleep(60)  # Hata durumunda 1 dakika bekle

def run_bot():
    """Bot'u başlat"""
    try:
        # Model'i başlangıçta yükle
        load_model_if_needed()
        
        # Bot uygulamasını oluştur
        application = Application.builder().token(TOKEN).build()

        # Komutları ekle
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

        # Web sunucusunu ayrı bir thread'de başlat
        web_thread = threading.Thread(target=start_web_server)
        web_thread.daemon = False
        web_thread.start()

        # Keep-alive thread'ini başlat
        if SERVICE_URL:
            keep_alive_thread = threading.Thread(target=keep_alive)
            keep_alive_thread.daemon = True
            keep_alive_thread.start()

        print("Bot ve web sunucusu başlatılıyor...")
        
        # Bot'u başlat
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False,
            stop_signals=None
        )
        
    except Exception as e:
        print(f"Bir hata oluştu: {str(e)}")
        time.sleep(30)
        print("Bot yeniden başlatılıyor...")
        run_bot()

if __name__ == '__main__':
    # Bot'u başlat
    run_bot() 