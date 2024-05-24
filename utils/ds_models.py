from typing import Dict
from math import ceil

from telegram import ReplyKeyboardMarkup


MODELS = {
    "Классическое обучение с учителем": ["Линейная регрессия", "Логистическая регрессия", "Метод ближайших соседей",
                                         "Случайный лес", "Градиентный бустинг"],
    "Рекомендательные системы": ["Коллаборативная фильтрация", "ALS", "LightFM", "BERT4Rec"],
    # "Компьютерное зрение": ["Convolutional Neural Network", "ResNet", "Детектирование объектов: YOLO",
    #                         "Сегментация: U-Net", "Vision Transformer", "Генеративные модели: Dall-E"],
    "Времянные ряды": ["Arima", "Facebook Prophet", "MLP based: NBEATS", "LSTM", "Temporal Fusion Transformer", "Deep AR"],
    "NLP": ["LSTM", "BERT", "GPT", "Wor2Vec", "FastText"],
    # "Кластеризация": ["K Means", "Аггломеративная кластеризация", "Иерархическая кластеризация", "DBSCAN"],
    # "Обучение с подкреплением": ["Cross-Entropy Method", "Multi-Armed Bandit", "Q Learning и DQN", "Actor Critic",
    #                              "On Policy methods: PPO"],
    # "Статистикa и A/B": ["Naive Bayes", "Generalized Linear Models (GLM)", "ANOVA", "T-test", "Коэффициенты корреляции"]
    "Свой запрос...": [],
}


def keys_to_response(d: Dict):
    items = list(d.keys())
    buttons_height = ceil(len(items) / 2)
    buttons = [items[(2 * i):(2 * (i + 1))] for i in range(buttons_height)]
    buttons.append(["Назад"])
    return ReplyKeyboardMarkup(buttons, one_time_keyboard=True)


def keys_to_filter(d: Dict):
    items = list(d.keys())
    return f"^({'|'.join(items)})$"


def items_to_response(d: Dict, text):
    if text in d:
        items = d[text]
        buttons_height = ceil(len(items) / 2)
        buttons = [items[(2*i):(2*(i+1))] for i in range(buttons_height)]
        buttons.append(["Назад"])
        return ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
