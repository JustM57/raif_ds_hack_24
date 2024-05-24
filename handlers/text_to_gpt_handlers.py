from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from config.openai_client import client
from utils.helpers import FINAL_CODE_EXAMPLE, USER_DATA_LOAD, CODE_EXAMPLE


code_example_buttons = [
    ["Посмотреть другой пример", "Назад", "Done"],
]
markup_code_example = ReplyKeyboardMarkup(code_example_buttons, one_time_keyboard=True)


user_data_code_example_buttons = [
    ["Загрузить фото датасета", "Назад", "Done"],
]
markup_user_data_code_example = ReplyKeyboardMarkup(user_data_code_example_buttons, one_time_keyboard=True)

spec_model_buttons = [
    ["Посмотреть пример кода", "Построить модель для своих данных"],
    ["Назад", "Done"],
]
markup_spec_model = ReplyKeyboardMarkup(spec_model_buttons, one_time_keyboard=True)


def text_request_to_gpt(user_prompt, system_prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_prompt}],
        max_tokens=1024,
        temperature=0.1,
    )
    reply = response.choices[0].message.content.strip()

    return reply


async def receive_model_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    text = update.message.text
    if text == "Назад":
        text = context.user_data["model"]
    context.user_data["model"] = text

    if not text == "Назад":
        await update.message.reply_text(f"Генерирую информацию по теме `{text}`...\nНеобходимо немного подождать.")
        prompt = f"Break down {text} topic in machine learning into smaller, easier-to-understand parts. " \
                 "Use formulas and examples of data to explain applicability. " \
                 "When I should use this machine learning model?"
        print(prompt)

        system_prompt = "Give answer in Russian language."
        reply = text_request_to_gpt(prompt, system_prompt)

        await update.message.reply_text(reply)
    await update.message.reply_text(
        "Можем посмотреть примеры кода по этой теме или попробовать сгенерировать решение с твоими данными.",
        reply_markup=markup_spec_model,
    )

    return CODE_EXAMPLE


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

        system_prompt = "Give answer in Russian language and the code in python language."
        reply = text_request_to_gpt(prompt, system_prompt)

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