
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import pytesseract
from PIL import Image
import io
import toolbottx  # Đảm bảo file này nằm cùng thư mục

BOT_TOKEN = "7680708362:AAHEjtbBRlvHzyh9CMal9I2cEhYkHq_BcFY"

# Cấu hình logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Chào bạn! Gửi ảnh kết quả Sunwin để mình dự đoán Tài/Xỉu.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    image_bytes = await photo_file.download_as_bytearray()

    image = Image.open(io.BytesIO(image_bytes))
    ocr_text = pytesseract.image_to_string(image)

    # Tách các từ là TÀI/XỈU
    extracted_tx = [word.strip().upper() for word in ocr_text.split() if word.strip().upper() in ["TÀI", "XỈU"]]

    if len(extracted_tx) < 5:
        await update.message.reply_text("Không tìm thấy đủ kết quả Tài/Xỉu trong ảnh.")
        return

    prediction, confidence = toolbottx.predict_taixiu(extracted_tx)
    result = f"Dự đoán: *{prediction}* với độ tin cậy {confidence:.1f}%"
    await update.message.reply_text(result, parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot đang chạy...")
    app.run_polling()

if __name__ == '__main__':
    main()
