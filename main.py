# Бот, который отвечает на Ваши вопросы на русском и английском языке + отправляет ответ голосовым, если ответ на английском

import os
import telebot
from deep_translator import GoogleTranslator
from gtts import gTTS
from openai import OpenAI

# Инициализация клиента API OpenAI с вашим API ключом
openai_client = OpenAI(
    api_key = "sk-eojihWMYuwlwO4oNjNMX8DbkkkBtLg7I",
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

# Функция для записи истории сообщений
def save_conversation_history_to_log(user_id, message):
    user = message.from_user
    if user.username:
        user = f"@{user.username}"
    else:
        user = f"У пользователя не установлен логин в Telegram, user_id = {message.chat.id}"
      
    with open("log.txt", "a", encoding="utf-8") as file:
        for msg in conversation_histories[user_id]:
            if msg["role"] == "user":
                role = f"Пользователь - {user}"
            else:
                role = "Бот"
            file.write(f"{role}: {msg['content']}\n")
        file.write(f"{'='*20}\n")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_input = message.text
    # user_name = message.from_user.username or "no username"

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

    # Создаем объект gTTS для преобразования текста в речь
    # https://gtts.readthedocs.io/en/latest/module.html#languages-gtts-lang
    if lang == 'en':
        tts = gTTS(ai_response_content, lang=lang)
        temp_file = "temp_audio.mp3"  # Создаем временный файл для сохранения аудио
        tts.save(temp_file) 
        # Отправляем аудио-сообщение - ответ пользователю 
        with open(temp_file, 'rb') as audio: 
            bot.send_voice(message.chat.id, audio) 
        # Удаляем временный файл 
        os.remove(temp_file) 
  
        # Переводим текст ответа с английского на русский и отправляем пользователю
        translated_text = GoogleTranslator(source='en', target='ru').translate(ai_response_content)
        bot.send_message(user_id, translated_text)
      
    # Добавление ответа нейронной сети в историю разговора
    conversation_history.append({"role": "system", "content": ai_response_content})

# После добавления ответа нейронной сети в историю, сохраняем всю историю разговора в log.txt
    save_conversation_history_to_log(user_id, message)

bot.polling()  # Запускаем бота
