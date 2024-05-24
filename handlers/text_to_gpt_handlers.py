from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
)
from config.openai_client import client
from utils.helpers import FINAL_CODE_EXAMPLE, CODE_EXAMPLE, CODE_EXAMPLE_WITH_USER_DATA

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
        temperature=0.2,
    )
    reply = response.choices[0].message.content.strip()

    return reply


async def receive_model_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    text = update.message.text
    if text != "Назад":
        # text = context.user_data["model"]
        context.user_data["model"] = text

        await update.message.reply_text(f"Генерирую информацию по теме `{context.user_data['model']}`"
                                        "\nНеобходимо немного подождать.⏳")
        prompt = f"Break down {context.user_data['model']} topic in machine learning into smaller, easier-to-understand parts. " \
                 "Use formulas and examples of data to explain applicability. " \
                 "When I should use this machine learning model?"
        print(prompt)

        system_prompt = "Give answer in Russian language. Do not use symbols `_`, `@` or `&`. " \
                        "Find all formulas in your answer and replace them " \
                        "with human readable format. For example pere-phrase formulas like this " \
                        "<$F = x_1 + x_2 + frac{1}{1 + e^x}$> to formulas like this <`F = x1 + x2 + 1/(1 + e^x)`>."
        reply = text_request_to_gpt(prompt, system_prompt)

        # controling_prompt = "Do not change content of this text. Find all formulas in it and replace them " \
        #                 "with human readable format. For example pere-phrase formulas like this " \
        #                 "<$F = x_1 + x_2 + frac{1}{1 + e^x}$> to formulas like this <`F = x1 + x2 + 1/(1 + e^x)`>."
        # reply = text_request_to_gpt(reply, controling_prompt)

        await update.message.reply_text(reply, parse_mode="Markdown")
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
        await update.message.reply_text(f"Генерирую пример кода для модели `{context.user_data['model']}` "
                                        "\nНеобходимо немного подождать.⏳")

        prompt = f"Provide an example on how to build solution using machine learning model {context.user_data['model']}. " \
                 "Start with providing data sample, correct preprocessing and end with getting predictions with the model."
        print(prompt)

        system_prompt = "Give answer in Russian language and the code in python language. Also do not use symbols `_`, `@` or `&`. "
        reply = text_request_to_gpt(prompt, system_prompt)

        await update.message.reply_text(reply, parse_mode="Markdown")
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

        return CODE_EXAMPLE_WITH_USER_DATA