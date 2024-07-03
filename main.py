import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import json

load_dotenv()

TOKEN = os.getenv("TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")

if not TOKEN or not BOT_USERNAME:
    raise ValueError("No TOKEN or BOT_USERNAME provided")

with open('trip_packages.json') as f:
    trip_packages = json.load(f)['trip_packages']


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Trip Packages and Ticket Sales Bot! Type /help to see available commands.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n/start - Start the bot\n/help - Show this help message\n/packages - Show available trip packages")


async def packages_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Hot Deals", callback_data='hot_deal')],
        [InlineKeyboardButton("Exclusive", callback_data='exclusive')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose a category:", reply_markup=reply_markup)


async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    category = query.data
    packages = [p for p in trip_packages if p['type'] == category]

    keyboard = [[InlineKeyboardButton(p['name'], callback_data=f"package_{p['id']}")] for p in packages]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=f"Available {category.replace('_', ' ').title()}:", reply_markup=reply_markup)


async def package_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    package_id = int(query.data.split('_')[1])
    package = next(p for p in trip_packages if p['id'] == package_id)

    await query.message.reply_photo(photo=package['photo_url'],
                                    caption=f"{package['name']}\nPrice: ${package['price']}\nDescription: {package['description']}")


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("packages", packages_command))
    application.add_handler(CallbackQueryHandler(category_handler, pattern='^(hot_deal|exclusive)$'))
    application.add_handler(CallbackQueryHandler(package_handler, pattern='^package_\\d+$'))

    application.run_polling()


if __name__ == "__main__":
    main()