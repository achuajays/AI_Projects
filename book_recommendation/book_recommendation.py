import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def search_books(query):
    """Search for books using OpenLibrary API"""
    url = f"http://openlibrary.org/search.json?q={query}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when user starts the bot"""
    await update.message.reply_text(
        "📚 Hello! I'm your Book Recommendation Bot.\n"
        "Send me a book topic or genre, and I'll find relevant books for you!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user's book topic request"""
    user_input = update.message.text
    books = search_books(user_input)

    if not books or not books.get('docs'):
        await update.message.reply_text("❌ No books found for this topic. Try another one!")
        return

    # Get top 5 books with authors
    top_books = []
    for book in books['docs'][:5]:
        title = book.get('title', 'Untitled')
        authors = ", ".join(book.get('author_name', ['Unknown Author']))
        top_books.append(f"• {title} by {authors}")

    # Generate AI-enhanced response using Groq
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system",
                 "content": "You are a knowledgeable librarian. Provide a brief, engaging description of these books."},
                {"role": "user",
                 "content": f"Topic: {user_input}\nBooks: {''.join(top_books)}\n\nWrite a short summary:"}
            ],
            model="llama3-70b-8192",
            temperature=0.7,
            max_tokens=500
        )
        summary = response.choices[0].message.content
    except Exception as e:
        summary = "Here are some great books I found:"

    # Format final message
    book_list = "\n".join(top_books)
    full_response = f"📖 {summary}\n\n{book_list}"

    await update.message.reply_text(full_response)


def main():
    """Start the bot"""
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        logger.error("Set TELEGRAM_BOT_TOKEN environment variable!")
        return

    app = Application.builder().token(telegram_token).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling
    app.run_polling()
    logger.info("Bot is running...")


if __name__ == "__main__":
    main()