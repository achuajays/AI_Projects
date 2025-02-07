import os
from dotenv import load_dotenv
from groq import Groq
from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load environment variables from .env file
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ")

# Initialize the groq client
client = Groq(api_key=GROQ_API_KEY)

# Create a custom reply keyboard with available commands
command_keyboard = ReplyKeyboardMarkup(
    [
        ["/question"],
        ["/answer"]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends a welcome message, instructions, and shows a custom keyboard with available commands.
    """
    welcome_message = (
        "Welcome to the <b>AI-Based Fun 'Would You Rather' Question Generator</b>! 🎮\n\n"
        "Use the <b>/question</b> command to get a creative question with two options.\n"
        "After answering, use <b>/answer &lt;your answer&gt;</b> to get a fun analysis of your choice.\n\n"
        "You can also use the buttons below to quickly send commands."
    )
    await update.message.reply_text(welcome_message, parse_mode=ParseMode.HTML, reply_markup=command_keyboard)


async def generate_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Generates a fun 'Would You Rather' question using groq API and sends it to the user.
    """
    groq_prompt = (
        "Generate a fun and creative 'Would You Rather' question. "
        "Include two clear options for the user to choose from. "
        "Make it entertaining and suitable for a game or social media post."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": groq_prompt}],
            temperature=0.8,
            max_completion_tokens=150,
            top_p=1,
            stop=None,
            stream=False,
        )
    except Exception as e:
        await update.message.reply_text(f"Error connecting to the AI API: {e}", parse_mode=ParseMode.HTML)
        return

    try:
        generated_text = completion.choices[0].message.content.strip()
    except Exception as e:
        await update.message.reply_text(f"Error processing the AI response: {e}", parse_mode=ParseMode.HTML)
        return

    await update.message.reply_text(generated_text, parse_mode=ParseMode.HTML)


async def analyze_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Analyzes the user's answer to a 'Would You Rather' question.
    The user must send the answer after the /answer command.
    """
    if context.args:
        user_answer = " ".join(context.args)
    else:
        await update.message.reply_text(
            "Please provide your answer after the command. Example:\n<code>/answer Option A</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    analysis_prompt = (
        f"Analyze the following answer to a 'Would You Rather' question: \"{user_answer}\". "
        "Provide fun and creative insights on what this answer might say about the person's preferences, personality, or decision-making style."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0.7,
            max_completion_tokens=150,
            top_p=1,
            stop=None,
            stream=False,
        )
    except Exception as e:
        await update.message.reply_text(f"Error connecting to the AI API for analysis: {e}", parse_mode=ParseMode.HTML)
        return

    try:
        analysis_result = completion.choices[0].message.content.strip()
    except Exception as e:
        await update.message.reply_text(f"Error processing the AI response for analysis: {e}",
                                        parse_mode=ParseMode.HTML)
        return

    await update.message.reply_text(analysis_result, parse_mode=ParseMode.HTML)


def main() -> None:
    """
    Starts the Telegram bot.
    """
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Command handler for /start
    application.add_handler(CommandHandler("start", start))
    # Command handler for /question
    application.add_handler(CommandHandler("question", generate_question))
    # Command handler for /answer
    application.add_handler(CommandHandler("answer", analyze_answer))

    print("Bot is running...")
    application.run_polling()


if __name__ == '__main__':
    main()