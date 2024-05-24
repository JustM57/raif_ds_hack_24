import json

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from utils.helpers import CHOOSING_DIRECTION


async def start_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # объект обновления
    update_obj = json.dumps(update.to_dict(), indent=4)

    # ответ
    reply = "*update object*\n\n" + "```json\n" + update_obj + "\n```"

    # перенаправление ответа в Telegram
    await update.message.reply_text(reply, parse_mode="Markdown")

    print("assistant:", reply)


direction_buttons = [
    ["Код графика по фото", "Справочник моделей"],
    ["Done"],
]
markup_direction = ReplyKeyboardMarkup(direction_buttons, one_time_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    await update.message.reply_text(
        "Привет!👋 Что хочешь изучить?📚",
        reply_markup=markup_direction,
    )

    return CHOOSING_DIRECTION


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data

    await update.message.reply_text(
        f"Был рад помочь, заходи еще!😉",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END
