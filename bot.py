import json
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

import logging

# URL сервера Flask
API_URL = 'http://localhost:5000/appointments'

DAYS = ["Вторник", "Среда", "Пятница"]
TIME_SLOTS = {
    "Вторник": ["12:00-13:00", "14:00-15:00", "15:00-16:00", "16:00-17:00"],
    "Среда": ["12:00-13:00", "14:00-15:00", "15:00-16:00", "16:00-17:00"],
    "Пятница": ["14:00-15:00", "15:00-16:00", "16:00-17:00"]
}

FIO, COURSE, SPECIALTY, PHONE, QUERY, EMOTIONAL_STATE, PREFERRED_METHODS, DAY_SELECTION, TIME_SELECTION, CONFIRMATION = range(10)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Работа с файлом database.json
def save_to_database(new_appointment):
    try:
        with open('database.json', 'r+', encoding='utf-8') as file:
            file_data = json.load(file)
            file_data['appointments'].append(new_appointment)
            file_data['count'] = len(file_data['appointments'])
            file.seek(0)
            json.dump(file_data, file, ensure_ascii=False, indent=4)
        logger.info("Data saved to database.json successfully")
    except FileNotFoundError:
        logger.error("Database file not found, creating a new file")
        with open('database.json', 'w', encoding='utf-8') as file:
            initial_data = {"count": 1, "appointments": [new_appointment]}
            json.dump(initial_data, file, ensure_ascii=False, indent=4)
    except json.JSONDecodeError:
        logger.error("JSON decode error in database.json, creating a new file")
        with open('database.json', 'w', encoding='utf-8') as file:
            initial_data = {"count": 1, "appointments": [new_appointment]}
            json.dump(initial_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.exception(f"An error occurred while saving to database.json: {e}")

# Работа с data.json
def save_to_data_file(new_appointment):
    try:
        with open('data.json', 'r+', encoding='utf-8') as file:
            file_data = json.load(file)
            file_data['appointments'].append(new_appointment)
            file_data['count'] = len(file_data['appointments'])
            file.seek(0)
            json.dump(file_data, file, ensure_ascii=False, indent=4)
        logger.info("Data saved to data.json successfully")
    except FileNotFoundError:
        logger.error("File not found, creating new file")
        with open('data.json', 'w', encoding='utf-8') as file:
            initial_data = {"count": 1, "appointments": [new_appointment]}
            json.dump(initial_data, file, ensure_ascii=False, indent=4)
    except json.JSONDecodeError:
        logger.error("JSON decode error in data.json, creating a new file")
        with open('data.json', 'w', encoding='utf-8') as file:
            initial_data = {"count": 1, "appointments": [new_appointment]}
            json.dump(initial_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.exception(f"An error occurred while saving to data.json: {e}")

# Функции обработки состояний
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Привет! Пожалуйста, введи следующие данные:\n1) ФИО")
    return FIO

async def fio(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    context.user_data['fio'] = update.message.text
    await update.message.reply_text("Теперь, пожалуйста, введи курс (например, 2):")
    return COURSE

async def course(update: Update, context: CallbackContext) -> int:
    context.user_data['course'] = update.message.text
    await update.message.reply_text("Введите специальность:")
    return SPECIALTY

async def specialty(update: Update, context: CallbackContext) -> int:
    context.user_data['specialty'] = update.message.text
    await update.message.reply_text("Введите контактный телефон:")
    return PHONE

async def phone(update: Update, context: CallbackContext) -> int:
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("С каким запросом Вы бы хотели обратиться к психологу?\n(Выберите вариант)")
    keyboard = [['Личное саморазвитие'], ['Семейные взаимоотношения'], ['Межличностные взаимоотношения'], ['Ситуация связанная с учебой'], ['Другое']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите один из вариантов:", reply_markup=reply_markup)
    return QUERY

async def query(update: Update, context: CallbackContext) -> int:
    context.user_data['query'] = update.message.text
    return await preferred_methods(update, context)

async def preferred_methods(update: Update, context: CallbackContext) -> int:
    context.user_data['query'] = update.message.text
    await update.message.reply_text("Какие методы в работе с психологом Вам ближе?")
    keyboard = [['Формат беседы'], ['Проективные техники'], ['Разбор на метафорических картах'], ['Коучинг']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите подходящий метод:", reply_markup=reply_markup)
    return DAY_SELECTION

async def day_selection(update: Update, context: CallbackContext) -> int:
    context.user_data['preferred_methods'] = update.message.text
    await update.message.reply_text("Выберите удобный день недели для консультации:")
    keyboard = [[day] for day in DAYS]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите день:", reply_markup=reply_markup)
    return TIME_SELECTION

async def time_selection(update: Update, context: CallbackContext) -> int:
    selected_day = update.message.text
    if selected_day not in DAYS:
        await update.message.reply_text("Выбранный день недоступен. Попробуйте снова.")
        return DAY_SELECTION

    context.user_data['day'] = selected_day
    response = requests.get(API_URL)
    if response.status_code != 200:
        await update.message.reply_text("Ошибка загрузки данных. Попробуйте позже.")
        return ConversationHandler.END

    data = response.json()
    taken_slots = [app['appointment']['time'] for app in data['appointments'] if app['appointment']['day'] == selected_day]
    available_slots = [slot for slot in TIME_SLOTS[selected_day] if slot not in taken_slots]

    if not available_slots:
        keyboard = [["Повторить"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Все временные слоты на этот день заняты. Пожалуйста, выберите другой день.", reply_markup=reply_markup)
        return DAY_SELECTION

    keyboard = [[slot] for slot in available_slots]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите время для консультации:", reply_markup=reply_markup)
    return CONFIRMATION

async def confirmation(update: Update, context: CallbackContext) -> int:
    selected_time = update.message.text
    context.user_data['time'] = selected_time

    new_appointment = {
        "fio": context.user_data['fio'],
        "course": context.user_data['course'],
        "specialty": context.user_data['specialty'],
        "phone": context.user_data['phone'],
        "query": context.user_data['query'],
        # "emotional_state": context.user_data.get('emotional_state', 'Не указано'),
        "preferred_methods": context.user_data.get('preferred_methods', 'Не указано'),
        "appointment": {
            "day": context.user_data['day'],
            "time": context.user_data['time']
        }
    }

    save_to_data_file(new_appointment)  # Сохранение в data.json
    save_to_database(new_appointment)  # Сохранение в database.json

    await update.message.reply_text(f"Вы успешно записаны на консультацию: {context.user_data['day']} {context.user_data['time']}.")
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Диалог завершен.")
    return ConversationHandler.END

async def count(update: Update, context: CallbackContext) -> None:
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        await update.message.reply_text(f"Текущее количество записей: {data['count']}")
    else:
        await update.message.reply_text("Ошибка при получении данных.")

def main():
    application = Application.builder().token('7799224730:AAFbdIWlKCHO24rsy_n1VLXKgR5-_2Ec1i0').build()

    application.add_handler(CommandHandler('count', count))
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, fio)],
            COURSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, course)],
            SPECIALTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, specialty)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, query)],
            PREFERRED_METHODS: [MessageHandler(filters.TEXT & ~filters.COMMAND, preferred_methods)],
            DAY_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, day_selection)],
            TIME_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, time_selection)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conversation_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
