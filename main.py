# Бот, который отвечает на Ваши вопросы на английском языке + отправляет то же сообщение голосовым

import telebot
import re

# Инициализация телеграм бота
TELEGRAM_BOT_TOKEN = '6829934856:AAGJHYKUmZiCESLaQmgeskdFMsp8w30gjP0'
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Текст, введённый латинскими буквами, преобразуется в кириллицу в соответствии с расположением букв на стандартной клавиатуре.\nЗаглавные латинские буквы после преобразования должны стать заглавными в кириллице. Текст, введённый в двойных кавычках, должен остаться латиницей.\n\nВведите текст латинскими буквами:")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    def latin_to_cyrillic(text):
        latin_keyboard = "qwertyuiop[]asdfghjkl;'zxcvbnm,./"
        cyrillic_keyboard = "йцукенгшщзхъфывапролджэячсмитьбю."
        translation = str.maketrans(latin_keyboard + latin_keyboard.upper(), cyrillic_keyboard + cyrillic_keyboard.upper())
        return text.translate(translation)

    # Функция, которая преобразует текст, за исключением частей в двойных кавычках
    def transform_text_except_quotes(text):
        parts = re.split('(".*?")', text)  # Разделение текста на части с учетом кавычек
        transformed_parts = [latin_to_cyrillic(part) if not part.startswith('"') else part for part in parts]
        return ''.join(transformed_parts)

    result = transform_text_except_quotes(message.text)
    bot.send_message(message.chat.id, result)

bot.infinity_polling()
