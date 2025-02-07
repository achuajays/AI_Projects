import os
import base64
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

load_dotenv()


# Groq API setup
GROQ_API_KEY = os.getenv("GROQ")
client = Groq(api_key=GROQ_API_KEY)

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Function to encode the image in base64
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# Function to generate hashtags from text
async def generate_hashtags_from_text(text: str) -> str:
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates relevant hashtags for social media posts."},
            {"role": "user", "content": f"Generate 5 relevant hashtags for this post: {text}"}
        ]
    )
    hashtags = response.choices[0].message.content
    return hashtags

# Function to generate caption and hashtags from an image
async def generate_caption_and_hashtags_from_image(image_bytes: bytes) -> str:
    # Encode the image in base64
    base64_image = encode_image(image_bytes)

    # Use Groq Vision API to analyze the image
    response = client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Generate  a good relevant caption and hashtags for the image: remember only generate caption and hashtag no explanation or summary "},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
    )
    caption_and_hashtags = response.choices[0].message.content
    return caption_and_hashtags

# Telegram command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me a text description or an image, and I'll generate hashtags and captions for you.")

# Telegram message handler for text
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    hashtags = await generate_hashtags_from_text(user_text)
    await update.message.reply_text(f"Generated Hashtags:\n{hashtags}")

# Telegram message handler for images
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the image file from the user's message
    photo = update.message.photo[-1]  # Get the highest resolution photo
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()

    # Generate caption and hashtags
    caption_and_hashtags = await generate_caption_and_hashtags_from_image(image_bytes)
    await update.message.reply_text(f"Caption and Hashtags:\n{caption_and_hashtags}")

# Main function to run the bot
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()