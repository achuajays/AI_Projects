import os
import requests
from dotenv import load_dotenv
from groq import Groq
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Load environment variables from .env file
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Base URL for TheMealDB API
MEALDB_BASE_URL = "https://www.themealdb.com/api/json/v1/1"

def search_meal_by_name(meal_name: str) -> dict:
    """
    Searches for a meal by name using TheMealDB API.
    Returns the first meal's details as a dict if found, otherwise returns None.
    """
    endpoint = f"{MEALDB_BASE_URL}/search.php?s={meal_name}"
    response = requests.get(endpoint)
    if response.status_code == 200:
        data = response.json()
        if data.get('meals'):
            return data['meals'][0]  # Return the first meal found
    print(f"Failed to fetch meal data for {meal_name}. Status code: {response.status_code}")
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends a welcome message and brief instructions.
    """
    welcome_message = (
        "Welcome to the <b>Smart Meal Planner Bot</b>!\n\n"
        "Send me a message describing what ingredients you have and your dietary or weight goals, "
        "and I'll suggest a recipe for you."
    )
    await update.message.reply_text(welcome_message, parse_mode=ParseMode.HTML)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Processes the user's message:
      1. Uses Groq to generate a recipe recommendation based on the description.
      2. Uses TheMealDB API to get recipe details.
      3. If not found, uses Groq to generate a custom recipe for the dish.
      4. Replies with the recipe information.
    """
    user_prompt = update.message.text.strip()
    if not user_prompt:
        await update.message.reply_text("Please provide a description of your ingredients and goals.", parse_mode=ParseMode.HTML)
        return

    # Step 1: Ask Groq to suggest a meal recipe name.
    groq_prompt = (
        "Based on the following details about available ingredients and dietary/weight goals, "
        "recommend a single meal recipe name that would best suit these requirements:\n\n"
        f"<b>Details:</b> {user_prompt}\n\n"
        "Provide only the recipe name. "
        "Remember to have no complex dish names—just an available dish name."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": groq_prompt}],
            temperature=0.6,
            max_completion_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )
    except Exception as e:
        await update.message.reply_text(f"Error connecting to Groq API: {e}", parse_mode=ParseMode.HTML)
        return

    try:
        recipe_name = completion.choices[0].message.content.strip()
    except Exception as e:
        await update.message.reply_text(f"Error processing Groq response: {e}", parse_mode=ParseMode.HTML)
        return

    if not recipe_name:
        await update.message.reply_text("Could not generate a recipe recommendation. Please try again.", parse_mode=ParseMode.HTML)
        return

    # Inform the user which recipe name was recommended.
    await update.message.reply_text(
        f"Recommended recipe: <b>{recipe_name}</b>\n\nFetching details...",
        parse_mode=ParseMode.HTML
    )

    # Step 2: Use TheMealDB API to fetch details about the recommended recipe.
    meal_details = search_meal_by_name(recipe_name)
    if not meal_details:
        # Step 3: If no recipe details are found, ask Groq to generate a full recipe.

        recipe_generation_prompt = (
            f"Generate a complete recipe for a dish called '{recipe_name}' based on the following details: {user_prompt}.\n\n"
            "Include a list of ingredients, step-by-step instructions, and any serving suggestions. "
            "Format the recipe clearly."
        )
        try:
            custom_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": recipe_generation_prompt}],
                temperature=0.6,
                max_completion_tokens=1024,
                top_p=1,
                stop=None,
                stream=False,
            )
            custom_recipe = custom_completion.choices[0].message.content.strip()
            await update.message.reply_text(custom_recipe.replace("**", " ").replace("*", " "), parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"Error generating custom recipe: {e}", parse_mode=ParseMode.HTML)
        return

    # Build a message with meal details from TheMealDB.
    response_message = (
        f"<b>Meal:</b> {meal_details.get('strMeal', 'N/A')}\n"
        f"<b>Category:</b> {meal_details.get('strCategory', 'N/A')}\n"
        f"<b>Area:</b> {meal_details.get('strArea', 'N/A')}\n\n"
        f"<b>Instructions:</b>\n{meal_details.get('strInstructions', 'N/A')}\n\n"
        f"<a href='{meal_details.get('strMealThumb', '')}'>Meal Image</a>"
    )

    # Step 4: Send the recipe details back to the user.
    await update.message.reply_text(response_message, parse_mode=ParseMode.HTML, disable_web_page_preview=False)

def main() -> None:
    """
    Runs the Telegram bot.
    """
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Command handler for /start
    application.add_handler(CommandHandler("start", start))
    # Message handler for any text message
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()