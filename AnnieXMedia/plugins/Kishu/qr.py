from pyrogram import filters
from pyrogram.types import Message
from AnnieXMedia import app
import qrcode
import io


def generate_qr_code(text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="white", back_color="black")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


@app.on_message(filters.command("qr"))
async def qr_handler(client, message: Message):
    if len(message.command) > 1:
        input_text = " ".join(message.command[1:])
        qr_image = generate_qr_code(input_text)
        await message.reply_photo(qr_image, caption="📷 Here's your QR Code")
    else:
        await message.reply_text("❌ Please provide the text for the QR code.\n\nExample: `/qr https://github.com/`")
