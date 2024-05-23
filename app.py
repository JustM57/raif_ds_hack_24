from telegram.ext import MessageHandler, CommandHandler, filters
from config.telegram_bot import application
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

CHOOSING_DIRECTION, CHOOSING_MODEL_CLASS, CHOOSING_PREPROCESSING_CLASS, CHOOSING_MODEL, CODE_EXAMPLE = range(5)


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

spec_model_buttons = [
    #["Посмотреть пример кода", "Построить модель для своих данных"],
    ["Назад", "Done"],
]
markup_spec_model = ReplyKeyboardMarkup(spec_model_buttons, one_time_keyboard=True)


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
    elif text == "Рекомендательные системы":
        # TODO: change markup
        reply_markup = markup_back
    else:
        reply_markup = None

    await update.message.reply_text(
        f"Вы выбрали {text.lower()}! Какую модель изучим по-подробнее?",
        reply_markup=reply_markup,
    )

    return CHOOSING_MODEL


async def receive_model_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text

    await update.message.reply_text("Генерирую информацию по теме...\nНеобходимо немного подождать.")
    prompt = f"Break down {text} topic in machine learning into smaller, easier-to-understand parts. " \
             "Use formulas and examples of data to explain applicability. " \
             "When I should use this machine learning model?"
    print(prompt)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Give answer in Russian language."},
            {"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.1,
    )
    reply = response.choices[0].message.content.strip()

    await update.message.reply_text(reply)
    await update.message.reply_text(
        "Можем посмотреть примеры кода по этой теме или попробовать сгенерировать решение с твоими данными.",
        reply_markup=markup_spec_model,
    )

    return CODE_EXAMPLE


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
                    filters.Regex("^Назад$"), second_stage
                ),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done), CommandHandler("end", done)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()