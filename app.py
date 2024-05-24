from config.telegram_bot import application

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from handlers.command_handlers import start, done
from handlers.image_to_gpt_handlers import code_example_with_user_data, chart_to_code
from handlers.text_to_gpt_handlers import code_example, receive_model_info
from utils.ds_models import keys_to_response, MODELS, items_to_response, keys_to_filter
from utils.helpers import CODE_EXAMPLE_WITH_USER_DATA, \
    FINAL_CODE_EXAMPLE, CODE_EXAMPLE, CHOOSING_MODEL, CHOOSING_MODEL_CLASS, \
    CHOOSING_DIRECTION, CHART_TO_CODE


markup_model_classes = keys_to_response(MODELS)

back_button = [
    ["Назад"],
]
markup_back = ReplyKeyboardMarkup(back_button, one_time_keyboard=True)

chart_load_buttons = [
    ["Загрузить фото графика", "Назад", "Done"],
]
markup_chart_load = ReplyKeyboardMarkup(chart_load_buttons, one_time_keyboard=True)


async def first_stage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    if text == "Назад":
        text = context.user_data["first"]
    context.user_data["first"] = text
    if text == "Код графика по фото":
        reply_markup = markup_chart_load
    elif text == "Справочник моделей":
        reply_markup = markup_model_classes
    else:
        reply_markup = None

    await update.message.reply_text(
        f"Вы выбрали {text.lower()}! Выбери интересующую тему.",
        reply_markup=reply_markup,
    )
    if text == "Код графика по фото":
        return CHART_TO_CODE
    elif text == "Справочник моделей":
        return CHOOSING_MODEL_CLASS


async def second_stage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    if text == "Назад":
        text = context.user_data["second"]
    context.user_data["second"] = text
    reply_markup = items_to_response(MODELS, text)

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


async def load_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """."""
    await update.message.reply_text(
        "Загрузите картинку графика, который вы хотели бы воспроизвести в виде кода.",
    )

    return CHART_TO_CODE


def main() -> None:
    """Run the bot."""

    # CHOOSING_DIRECTION, CHOOSING_MODEL_CLASS, CHOOSING_MODEL, CODE_EXAMPLE
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_DIRECTION: [
                MessageHandler(
                    filters.Regex("^(Код графика по фото|Справочник моделей)$"), first_stage
                ),
                # MessageHandler(filters.Regex("^Something else...$"), custom_choice),
            ],
            CHART_TO_CODE: [
                MessageHandler(
                    filters.Regex("^Загрузить фото графика"), load_chart
                ),
                MessageHandler(
                    filters.PHOTO | filters.Regex("^Посмотреть другой пример$"), chart_to_code
                ),
                MessageHandler(
                    filters.Regex("^Назад$"), start
                ),
            ],
            CHOOSING_MODEL_CLASS: [
                MessageHandler(
                    filters.Regex(keys_to_filter(MODELS)), second_stage
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
            CODE_EXAMPLE_WITH_USER_DATA: [
                MessageHandler(
                    filters.Regex("^Загрузить фото датасета$"), code_example_with_user_data_start
                ),
                MessageHandler(
                    filters.PHOTO | filters.Regex("^Посмотреть другой пример$"), code_example_with_user_data
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