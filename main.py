from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.constants import ParseMode
from database_management import add_user_start
from sendDM import start_dm_service, stop_dm_service
from subscribe import payment_start, button_handler
from callback import address_message_handler, text_message_handler




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['subscribe_input_flag'] = False
    await add_user_start(update=update, context=context)
    message = (
        "🎉 *Welcome to CryptoAdvisor Bot!*\n\n"
        "I'm here to help you track and analyze cryptocurrencies.\n"
        "Run /help to see all available commands."
    )
    await update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.message.from_user.first_name
    await update.message.reply_text(f'Hello {user_name}! How can I assist you today?')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "🤖 *Welcome to CryptoAdvisor Bot!*\n\n"
        "I am your AI-powered cryptocurrency market assistant. Here's what I can do for you:\n\n"
        "📊 *Key Features:*\n"
        "• Real-time cryptocurrency analysis and monitoring\n"
        "• Market trend detection and insights\n" 
        "• Detailed metrics including market cap, volume, ATH\n"
        "• AI-powered price movement predictions\n"
        "• Premium features available via subscription\n\n"
        "🔍 *Available Commands:*\n"
        "• /start - Begin interaction\n"
        "• /hello - Get a greeting\n"
        "• /help - Show this help message\n"
        "• /subscribe - Access premium features\n\n"
        "Simply send me a token address to get detailed analytics!"
    )
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def start_sendDm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start_dm_service()
async def stop_sendDm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await stop_dm_service()

async def start_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['subscribe_input_flag'] = True
    await payment_start(update=update, context=context)

def main():
    # Load bot token from environment variable or config file in production
    application = ApplicationBuilder().token('7904308436:AAFDqx7xPPi59E7LI4Pe9GfniR1D9NGMTz4').build()

    # Add handlers
    application.add_handler(CommandHandler("hello", hello))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("subscribe", start_payment))
    application.add_handler(CommandHandler("start_sendDm", start_sendDm))
    application.add_handler(CommandHandler("stop_sendDm", stop_sendDm))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    # application.add_handler(MessageHandler(filters.TEXT, message_handler))
    application.add_handler(MessageHandler(filters.Regex(r'\A[0-9A-Fa-fx]+\Z'), address_message_handler))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    # Start the Bot
    print("👟👟Bot is running...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
