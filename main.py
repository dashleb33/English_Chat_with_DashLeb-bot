# Бот, который отвечает на Ваши вопросы на английском языке + отправляет то же сообщение голосовым

import os
from io import BytesIO

import telebot
# import googletrans
# from googletrans import Translator
from textblob import TextBlob
from gtts import gTTS
from openai import OpenAI

# Инициализация клиента API OpenAI с вашим API ключом
openai_client = OpenAI(
    api_key = "sk-ocZsDK2UM23MfVob1ncrgijjrEytVdeU",  # Замените на ваш API ключ 
    base_url = "https://api.proxyapi.ru/openai/v1",
  )

# Here is the token for bot English Chat with DashLeb-bot @English_Chat_with_DashLeb_bot: 
TOKEN = '6562179822:AAHu3pMM4SN6am9aQDRTy3H38nUICCMoacI'
bot = telebot.TeleBot(TOKEN)

  # Словарь для хранения истории разговора с каждым пользователем
conversation_histories = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! \nЯ бот, который отвечает на Ваши вопросы на английском либо русском языке. \nЗадайте Ваш вопрос. \n\nHi! I am a bot that answers your questions in English or Russian. \nAsk your question.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_input = message.text

    # Если история для пользователя не существует, создаем новую
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []

    # Добавление ввода пользователя в историю разговора
    conversation_history = conversation_histories[user_id]
    conversation_history.append({"role": "user", "content": user_input})

    # Отправка запроса в нейронную сеть
    chat_completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=conversation_history
      )

    # Извлечение и ответ на сообщение пользователя
    ai_response_content = chat_completion.choices[0].message.content

    # Отправляем ответ пользователю в Telegram
    bot.send_message(user_id, ai_response_content)

    # Определяем язык ответа: если нет ни одной русской буквы => английский, иначе - русский
    russian_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    lang = 'en'
    for char in ai_response_content.lower():
        if char in russian_letters:
            lang = 'ru'
            break
          
    # Если язык ответа английский, формируем и выводим перевод на русский
    # if lang == 'en':
        # translator = Translator()
        # translated_text = translator.translate(ai_response_content, src='en', dest='ru').text
        # Отправляем перевод пользователю в Telegram
        # bot.send_message(user_id, translated_text)

    # Создаем объект gTTS для преобразования текста в речь
    # https://gtts.readthedocs.io/en/latest/module.html#languages-gtts-lang
    if lang == 'en':
        tts = gTTS(ai_response_content, lang=lang)  # Можете изменить язык на нужный вам
        # Создаем временный файл для сохранения аудио
        temp_file = "temp_audio.mp3"
        tts.save(temp_file)
        # Отправляем аудио-сообщение - тот же ответ пользователю
        with open(temp_file, 'rb') as audio:
            bot.send_voice(message.chat.id, audio)
        # Удаляем временный файл
        os.remove(temp_file)

    # Добавление ответа нейронной сети в историю разговора
    conversation_history.append({"role": "system", "content": ai_response_content})

# Запускаем бота
bot.polling()