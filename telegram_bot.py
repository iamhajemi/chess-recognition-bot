#!/usr/bin/env python3

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from recognize import predict_chessboard, load_model_if_needed
import tempfile
import time
import chess
import chess.engine
from flask import Flask, request, Response
import asyncio
from quart import Quart, request, Response

# Quart uygulamasını oluştur (Flask'ın async versiyonu)
app = Quart(__name__)

# Loglama ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot token'ınızı buraya girin
TOKEN = "7563812107:AAHX2ADgHEkHLjnBFpCXoqvq2LcqO7TB_YQ"

# Stockfish yolu
STOCKFISH_PATH = "./stockfish"

# Global bot uygulaması
bot_app = None

def create_bot_app():
    global bot_app
    if bot_app is None:
        bot_app = Application.builder().token(TOKEN).build()
        # Komutları ekle
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("help", help_command))
        bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    return bot_app

def analyze_position(fen):
    """Stockfish ile pozisyonu analiz et"""
    try:
        # Stockfish motorunu başlat
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        
        # Motor ayarlarını yap - Bellek kullanımını azalt
        engine.configure({
            "Threads": 1,           # CPU thread sayısını azalt
            "Hash": 32,            # Hash tablosu boyutunu azalt (MB)
            "Skill Level": 20,     # En yüksek seviye
            "Move Overhead": 1000,  # Hamle başına düşünme süresi (ms)
            "UCI_ShowWDL": True,    # Kazanma/Beraberlik/Kaybetme oranlarını göster
            "MultiPV": 1,          # Sadece en iyi hamleyi göster
            "Ponder": False        # Arka planda düşünmeyi kapat
        })
        
        # Tahtayı FEN'den oluştur
        board = chess.Board(fen)
        
        # Analiz yap (derinlik ve süreyi azalt)
        info = engine.analyse(board, chess.engine.Limit(depth=15, time=5.0))
        
        # En iyi hamleyi ve puanı al
        best_move = info["pv"][0]
        score = info["score"].relative.score(mate_score=100000)
        
        # Varyasyonu al (sadece ilk 2 hamle)
        variation = board.variation_san(info["pv"][:2])
        
        # WDL (Kazanma/Beraberlik/Kaybetme) oranlarını al
        wdl = info.get("wdl", None)
        
        # Hamleyi insan tarafından okunabilir formata çevir
        move_san = board.san(best_move)
        
        # Motoru kapat
        engine.quit()
        
        # Sonucu formatla
        if score is not None:
            score_str = f"{score/100:.2f}" if abs(score) < 100000 else "Mat"
            wdl_str = f"\nKazanma/Beraberlik/Kaybetme: {wdl[0]}%/{wdl[1]}%/{wdl[2]}%" if wdl else ""
            return (
                f"En iyi hamle: {move_san} (Değerlendirme: {score_str})\n"
                f"Önerilen varyasyon: {variation}\n"
                f"Analiz derinliği: 15{wdl_str}"
            )
        else:
            return f"En iyi hamle: {move_san}\nÖnerilen varyasyon: {variation}\nAnaliz derinliği: 15"
            
    except Exception as e:
        return f"Analiz sırasında bir hata oluştu: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot başlatıldığında çalışacak komut"""
    # Model'i başlangıçta yükle
    load_model_if_needed()
    await update.message.reply_text(
        'Merhaba! Ben bir satranç tahtası tanıma botuyum. '
        'Bana bir satranç tahtası fotoğrafı gönder, ben sana FEN notasyonunu ve en iyi hamleyi söyleyeyim.'
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
            fen = predict_chessboard(temp_file, type('Args', (), {'quiet': True, 'debug': False})())
            
            # FEN notasyonunu gönder
            await update.message.reply_text(f"FEN Notasyonu:\n`{fen}`", parse_mode='Markdown')
            
            # Lichess analiz linki
            lichess_url = f"https://lichess.org/analysis/standard/{fen}"
            await update.message.reply_text(f"Lichess'te analiz et:\n{lichess_url}")
            
            # Stockfish analizi
            analysis = analyze_position(fen)  # await kaldırıldı
            await update.message.reply_text(analysis)
            
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

@app.route('/')
async def health_check():
    return 'Bot çalışıyor!', 200

@app.route(f'/{TOKEN}', methods=['POST'])
async def webhook():
    """Telegram'dan gelen webhook isteklerini işle"""
    if request.method == "POST":
        json_data = await request.get_json()
        update = Update.de_json(json_data, create_bot_app().bot)
        await create_bot_app().process_update(update)
        return Response('ok', status=200)
    return Response('', status=404)

# Model'i başlangıçta yükle
load_model_if_needed()

async def setup_webhook():
    """Webhook'u ayarla"""
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', f'https://chess-recognition-bot.onrender.com/{TOKEN}')
    await create_bot_app().bot.set_webhook(url=WEBHOOK_URL)
    print(f"Webhook set to {WEBHOOK_URL}")

if __name__ == '__main__':
    # Webhook'u ayarla
    asyncio.run(setup_webhook())
    
    # Quart uygulamasını başlat
    app.run(host='0.0.0.0', port=8000) 