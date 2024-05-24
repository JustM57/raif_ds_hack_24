from telegram import Update
from telegram.ext import (
    ContextTypes,
)
from config.openai_client import client
from handlers.text_to_gpt_handlers import markup_code_example
from utils.helpers import CODE_EXAMPLE_WITH_USER_DATA, CHART_TO_CODE


def image_request_to_gpt(image_file, prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "Give answer in Russian language and the code in python language."},
            {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_file,
                    },
                },
            ]},
        ],
        max_tokens=1024,
        temperature=0.5,
    )
    reply = response.choices[0].message.content.strip()

    return reply


async def code_example_with_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """."""
    if not (update.message.text and update.message.text == "Посмотреть другой пример"):
        image_file = await context.bot.get_file(update.message.photo[-1].file_id)
        context.user_data["photo"] = image_file

    await update.message.reply_text(f"Генерирую пример кода для модели {context.user_data['model']}... "
                                    "\nНеобходимо немного подождать.")

    prompt = f"Provide an example on how to build solution using machine learning model {context.user_data['model']}. " \
             "If the image contains the dataset then use it as input data sample for the problem solution. " \
             "If there is no dataset on the image return `NO DATASET`"

    reply = image_request_to_gpt(context.user_data["photo"].file_path, prompt)

    if reply != 'NO DATASET':
        await update.message.reply_text(reply)
        await update.message.reply_text(
            "Если код не подходит, можно попробовать сгенерировать его заново.",
            reply_markup=markup_code_example,
        )

    else:
        await update.message.reply_text(
            "Не смог обнаружить датасет на фото. "
            "Попробуй загрузить другую картинку.",
        )

    return CODE_EXAMPLE_WITH_USER_DATA


async def chart_to_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """."""
    if not (update.message.text and update.message.text == "Посмотреть другой пример"):
        image_file = await context.bot.get_file(update.message.photo[-1].file_id)
        context.user_data["chart_photo"] = image_file

    await update.message.reply_text(f"Генерирую код для построения графика... "
                                    "\nНеобходимо немного подождать.")

    prompt = f"If the image contains the chart on it then return python code how to plot such chart, "\
             "what data should look like to be able to plot the chart and the preview of it. "\
             "If there is no charts on the image return `NO CHART`"

    reply = image_request_to_gpt(context.user_data["chart_photo"].file_path, prompt)

    if reply != 'NO CHART':
        await update.message.reply_text(reply)
        await update.message.reply_text(
            "Если код не подходит, можно попробовать сгенерировать его заново.",
            reply_markup=markup_code_example,
        )

    else:
        await update.message.reply_text(
            "Не смог обнаружить график на фото. "
            "Попробуй загрузить другую картинку.",
        )

    return CHART_TO_CODE
