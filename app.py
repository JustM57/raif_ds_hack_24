from telegram.ext import MessageHandler, CommandHandler, filters
from config.telegram_bot import application
import base64
from telegram import Update
from config.openai_client import client
# from handlers.message_handlers import chatgpt_reply
# from handlers.command_handlers import start_reply
#
# # Регистрация обработчика текстовых сообщений
# message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, chatgpt_reply)
# application.add_handler(message_handler)
#
# # Регистрация обработчика команд
# start_command_handler = CommandHandler("start", start_reply)
# application.add_handler(start_command_handler)
#
# # Запуск бота
# application.run_polling()


from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from handlers.image_to_gpt_handlers import code_example_with_user_data
from handlers.text_to_gpt_handlers import code_example, receive_model_info
from utils.helpers import FINAL_CODE_EXAMPLE_WITH_USER_DATA, CODE_EXAMPLE_WITH_USER_DATA, USER_DATA_LOAD, \
    FINAL_CODE_EXAMPLE, CODE_EXAMPLE, CHOOSING_MODEL, CHOOSING_MODEL_CLASS, CHOOSING_PREPROCESSING_CLASS, \
    CHOOSING_DIRECTION


direction_buttons = [
    ["Препроцессинг", "Модели"],
    ["Done"],
]
markup_direction = ReplyKeyboardMarkup(direction_buttons, one_time_keyboard=True)

model_class_buttons = [
    ["Классическое обучение с учителем"],
    ["Рекомендательные системы"],
    ["..."],
    ["Назад"],
]
markup_model_classes = ReplyKeyboardMarkup(model_class_buttons, one_time_keyboard=True)

back_button = [
    ["Назад"],
]
markup_back = ReplyKeyboardMarkup(back_button, one_time_keyboard=True)

classic_models_buttons = [
    ["Линейные модели", "Метрические методы"],
    ["Решающие деревья", "Ансамбли в машинном обучении"],
    ["Градиентный бустинг"],
    ["Назад"],
]
markup_classic_models = ReplyKeyboardMarkup(classic_models_buttons, one_time_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    await update.message.reply_text(
        "Привет! Что хочешь изучить?",
        reply_markup=markup_direction,
    )

    return CHOOSING_DIRECTION


async def back_to_direction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Back to CHOOSING_DIRECTION."""

    return CHOOSING_DIRECTION


async def first_stage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    if text == "Назад":
        text = context.user_data["first"]
    context.user_data["first"] = text
    if text == "Препроцессинг":
        # TODO: change markup
        reply_markup = markup_back
    elif text == "Модели":
        reply_markup = markup_model_classes
    else:
        reply_markup = None

    await update.message.reply_text(
        f"Вы выбрали {text.lower()}! Выбери интересующую тему.",
        reply_markup=reply_markup,
    )
    if text == "Препроцессинг":
        return CHOOSING_PREPROCESSING_CLASS
    elif text == "Модели":
        return CHOOSING_MODEL_CLASS


async def second_stage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    if text == "Назад":
        text = context.user_data["second"]
    context.user_data["second"] = text
    if text == "Классическое обучение с учителем":
        reply_markup = markup_classic_models
    elif text == "Рекомендательные системы" or text == "...":
        # TODO: change markup
        reply_markup = markup_back
    else:
        reply_markup = None

    await update.message.reply_text(
        f"Вы выбрали {text.lower()}! Какую модель изучим по-подробнее?",
        reply_markup=reply_markup,
    )

    return CHOOSING_MODEL


async def code_example_with_user_data_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """."""
    await update.message.reply_text(
        "Загрузите скриншот датафрейма для генерации примера.",
    )

    return CODE_EXAMPLE_WITH_USER_DATA


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data

    await update.message.reply_text(
        f"Был рад помочь, заходи еще!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""

    # CHOOSING_DIRECTION, CHOOSING_MODEL_CLASS, CHOOSING_MODEL, CODE_EXAMPLE
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_DIRECTION: [
                MessageHandler(
                    filters.Regex("^(Препроцессинг|Модели)$"), first_stage
                ),
                # MessageHandler(filters.Regex("^Something else...$"), custom_choice),
            ],
            CHOOSING_PREPROCESSING_CLASS: [
                MessageHandler(
                    filters.Regex("^Назад$"), start
                ),
            ],
            CHOOSING_MODEL_CLASS: [
                MessageHandler(
                    filters.Regex("^(Классическое обучение с учителем|Рекомендательные системы)$"), second_stage
                ),
                MessageHandler(
                    filters.Regex("^Назад$"), start
                ),
            ],
            CHOOSING_MODEL: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$") | filters.Regex("^Назад$")),
                    receive_model_info
                ),
                MessageHandler(
                    filters.Regex("^Назад$"), first_stage
                ),
            ],
            CODE_EXAMPLE: [
                MessageHandler(
                    filters.Regex("^(Посмотреть пример кода|Построить модель для своих данных)$"), code_example
                ),
                MessageHandler(
                    filters.Regex("^Назад$"), second_stage
                ),
            ],
            FINAL_CODE_EXAMPLE: [
                MessageHandler(
                    filters.Regex("^Посмотреть другой пример$"), code_example
                ),
                MessageHandler(
                    filters.Regex("^Назад$"), receive_model_info
                ),
            ],
            USER_DATA_LOAD: [
                MessageHandler(
                    filters.Regex("^Загрузить фото датасета$"), code_example_with_user_data_start
                ),
                MessageHandler(
                    filters.Regex("^Назад$"), receive_model_info
                ),
            ],
            CODE_EXAMPLE_WITH_USER_DATA: [
                MessageHandler(
                    filters.PHOTO | filters.Regex("^Посмотреть другой пример$"), code_example_with_user_data
                )
            ],
            FINAL_CODE_EXAMPLE_WITH_USER_DATA: [
                MessageHandler(
                    filters.Regex("^Посмотреть другой пример$"), code_example_with_user_data
                ),
                MessageHandler(
                    filters.Regex("^Назад$"), receive_model_info
                ),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done), CommandHandler("end", done)],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()