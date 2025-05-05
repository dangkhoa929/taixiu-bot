
import logging
import re
import pytesseract
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "YOUR_TOKEN_HERE"  # Replace with your actual token

history = []

def extract_score_from_image(image_data):
    image = Image.open(BytesIO(image_data)).convert("L")
    open_cv_image = np.array(image)
    text = pytesseract.image_to_string(open_cv_image, config="--psm 6 digits")
    result = re.findall(r"\d+", text)
    return result

def convert_to_tx(result_list):
    tx = []
    for num in result_list:
        if num.isdigit():
            tx.append("T" if int(num) % 2 == 1 else "X")
    return tx

def predict_next(tx_list):
    if len(tx_list) < 3:
        return "Không đủ dữ liệu để dự đoán."
    last = tx_list[-1]
    if tx_list[-3:] == ["T", "T", "T"]:
        return "Dự đoán: Xỉu"
    elif tx_list[-3:] == ["X", "X", "X"]:
        return "Dự đoán: Tài"
    else:
        return f"Dự đoán theo mẫu: {'Tài' if last == 'X' else 'Xỉu'}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Gửi ảnh kết quả SunWin để bot dự đoán!")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.photo[-1].get_file()
    image_bytes = await file.download_as_bytearray()
    result_list = extract_score_from_image(image_bytes)
    tx_list = convert_to_tx(result_list)
    history.extend(tx_list)
    prediction = predict_next(history)
    response = f"Kết quả: {' '.join(tx_list)}\n{prediction}"
    await update.message.reply_text(response)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.run_polling()

if __name__ == "__main__":
    main()
