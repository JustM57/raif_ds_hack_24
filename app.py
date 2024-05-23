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

(
    CHOOSING_DIRECTION,
    CHOOSING_MODEL_CLASS,
    CHOOSING_PREPROCESSING_CLASS,
    CHOOSING_MODEL,
    CODE_EXAMPLE,
    FINAL_CODE_EXAMPLE,
    USER_DATA_LOAD,
    CODE_EXAMPLE_WITH_USER_DATA,
    FINAL_CODE_EXAMPLE_WITH_USER_DATA,
) = range(9)


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
    ["Посмотреть пример кода", "Построить модель для своих данных"],
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


async def receive_model_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    text = update.message.text
    if text == "Назад":
        text = context.user_data["model"]
    context.user_data["model"] = text

    if not text == "Назад":
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


code_example_buttons = [
    ["Посмотреть другой пример", "Назад", "Done"],
]
markup_code_example = ReplyKeyboardMarkup(code_example_buttons, one_time_keyboard=True)


user_data_code_example_buttons = [
    ["Загрузить фото датасета", "Назад", "Done"],
]
markup_user_data_code_example = ReplyKeyboardMarkup(user_data_code_example_buttons, one_time_keyboard=True)


async def code_example(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """."""
    text = update.message.text
    if text == "Назад":
        text = context.user_data["code_example"]
    context.user_data["code_example"] = text

    if text == "Посмотреть пример кода" or text == "Посмотреть другой пример":
        await update.message.reply_text(f"Генерирую пример кода для модели {context.user_data['model']}... "
                                        "\nНеобходимо немного подождать.")

        prompt = f"Provide an example on how to build solution using machine learning model {context.user_data['model']}. " \
                 "Start with providing data sample, correct preprocessing and end with getting predictions with the model."
        print(prompt)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Give answer in Russian language and the code in python language."},
                      {"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.5,
        )
        reply = response.choices[0].message.content.strip()

        await update.message.reply_text(reply)
        await update.message.reply_text(
            "Если код не подходит, можно попробовать сгенерировать его заново.",
            reply_markup=markup_code_example,
        )

        return FINAL_CODE_EXAMPLE

    elif text == "Построить модель для своих данных":
        await update.message.reply_text(
            "Для построения примера с вашими данными необходимо загрузить скриншот датафрейма.",
            reply_markup=markup_user_data_code_example,
        )

        return USER_DATA_LOAD


async def code_example_with_user_data_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """."""
    await update.message.reply_text(
        "Загрузите скриншот датафрейма для генерации примера.",
    )

    return CODE_EXAMPLE_WITH_USER_DATA


def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


async def code_example_with_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """."""
    if not (update.message.text and update.message.text == "Посмотреть другой пример"):
        new_file = await update.message.effective_attachment[-1].get_file()
        image_path = await new_file.download_to_drive()

        base64_image = encode_image(image_path)
        context.user_data["photo"] = base64_image

    await update.message.reply_text(f"Генерирую пример кода для модели {context.user_data['model']}... "
                                    "\nНеобходимо немного подождать.")

    prompt = f"Provide an example on how to build solution using machine learning model {context.user_data['model']}. " \
             "If the image contains the dataset then use it as input data sample for the problem solution. " \
             "If there is no dataset on the image return `NO DATASET`"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{context.user_data['photo']}",
                    },
                },
            ]},
        ],
        max_tokens=1024,
        temperature=0.5,
    )
    reply = response.choices[0].message.content.strip()

    if reply != 'NO DATASET':
        await update.message.reply_text(reply)
        await update.message.reply_text(
            "Если код не подходит, можно попробовать сгенерировать его заново.",
            reply_markup=markup_code_example,
        )

        return FINAL_CODE_EXAMPLE_WITH_USER_DATA
    else:
        await update.message.reply_text(
            "Не смог обнаружить датасет на фото. "
            "Попробуй загрузить другую картинку.",
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
                    filters.PHOTO, code_example_with_user_data
                )
            ],
            FINAL_CODE_EXAMPLE_WITH_USER_DATA: [
                MessageHandler(
                    filters.Regex("^Посмотреть другой пример$"), code_example
                ),
                MessageHandler(
                    filters.Regex("^Назад$"), code_example_with_user_data_start
                ),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done), CommandHandler("end", done)],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()