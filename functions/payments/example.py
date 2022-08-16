"""Basic example for a bot that can receive payment from user."""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Update
from telegram import LabeledPrice

from telegram.ext import CommandHandler, PreCheckoutQueryHandler, CallbackQueryHandler
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

from telegram.error import BadRequest

from os import environ

from base_template.keyboards import INVOICE_EDITOR_KEYBOARD

from functions.payments.table.queries import get_data, db_connect, remove_invoice

BACK = '<<'
FORWARD = '>>'
MORE = 'Подробнее'

INVOICE_BACK = '<<<'
INVOICE_FORWARD = '>>>'
DELETE = 'Удалить'
EDIT = 'Изменить'


def generate_keyboard():
    return [[InlineKeyboardButton(BACK, callback_data=BACK),
             InlineKeyboardButton(MORE, callback_data=MORE),
             InlineKeyboardButton(FORWARD, callback_data=FORWARD)]]


def generate_invoice_keyboard():
    return [[InlineKeyboardButton(INVOICE_BACK, callback_data=INVOICE_BACK),
             InlineKeyboardButton(EDIT, callback_data=EDIT),
             InlineKeyboardButton(DELETE, callback_data=DELETE),
             InlineKeyboardButton(INVOICE_FORWARD, callback_data=INVOICE_FORWARD)]]


def start(update: Update, ctx: CallbackContext) -> None:
    update.message.reply_text("Купить сертификат /buy\n"
                              "Посмотреть все товары /carousel")


def show_carousel(update: Update, ctx: CallbackContext, admin=False) -> None:
    """Показывает "карусель" с определённым индексом"""
    chat_id = update.message.chat_id

    data = get_data(db_connect())

    if admin:
        if len(data) == 0:
            ctx.bot.send_message(chat_id=chat_id,
                                 text="Вы еще не добавили ни одного товара на витрину.")
            return

        if len(data) == 1:
            keyboard = [[InlineKeyboardButton(EDIT, callback_data=EDIT),
                         InlineKeyboardButton(DELETE, callback_data=DELETE)]]
        else:
            keyboard = generate_invoice_keyboard()
    else:
        if len(data) == 0:
            ctx.bot.send_message(chat_id=chat_id,
                                 text="Товары в магазине закончились. Ждём новых поставок.\n"
                                      "Просим прощения за предоставленные неудобства.")
            return

        if len(data) == 1:
            keyboard = [[InlineKeyboardButton(MORE, callback_data=MORE)]]
        else:
            keyboard = generate_keyboard()

    text = data[0]['long_description'].replace('\\n', '\n')

    message = ctx.bot.send_message(chat_id=chat_id, text=text,
                                   reply_markup=InlineKeyboardMarkup(keyboard, resize_keyboard=True))

    ctx.user_data[f"carousel_index_{str(message['date']).split('+')[0]}"] = 0


def keyboard_callback_handler(update: Update, ctx: CallbackContext) -> None:
    """обработка коллбеков копок"""
    query = update.callback_query
    query_data = query.data

    data = get_data(db_connect())

    query.answer()

    if "carousel_index" not in ctx.user_data:
        ctx.user_data["carousel_index"] = 0

    if query_data == MORE:
        query.delete_message()
        create_invoice(update, ctx, data[ctx.user_data["carousel_index"]], query.message.chat_id)
        return

    time = str(query.message.date).split('+')[0]
    text = data[ctx.user_data[f"carousel_index_{time}"]]['long_description'].replace('\\n', '\n')

    try:
        if query_data == FORWARD:
            ctx.user_data[f"carousel_index_{time}"] += 1
            ctx.user_data[f"carousel_index_{time}"] %= len(data)
            query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(generate_keyboard()))

        elif query_data == BACK:
            ctx.user_data[f"carousel_index_{time}"] -= 1
            ctx.user_data[f"carousel_index_{time}"] %= len(data)
            query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(generate_keyboard()))

        elif query_data == INVOICE_FORWARD:
            ctx.user_data[f"carousel_index_{time}"] += 1
            ctx.user_data[f"carousel_index_{time}"] %= len(data)
            query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(generate_invoice_keyboard()))

        elif query_data == INVOICE_BACK:
            ctx.user_data[f"carousel_index_{time}"] -= 1
            ctx.user_data[f"carousel_index_{time}"] %= len(data)
            query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(generate_invoice_keyboard()))

        elif query_data == DELETE:
            if len(data) > 1:
                remove_invoice(db_connect(), data[ctx.user_data[f"carousel_index_{time}"]]['title'])

                data.pop(ctx.user_data[f"carousel_index_{time}"])
                print(data, ctx.user_data[f"carousel_index_{time}"])
                ctx.user_data[f"carousel_index_{time}"] = 0

                text = data[ctx.user_data[f"carousel_index_{time}"]]['long_description'].replace('\\n', '\n')
                print(text)
                query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(generate_invoice_keyboard()))
            elif len(data) == 1:
                remove_invoice(db_connect(), data[ctx.user_data[f"carousel_index_{time}"]]['title'])
                data.pop(ctx.user_data[f"carousel_index_{time}"])
                del ctx.user_data[f"carousel_index_{time}"]
                query.edit_message_text(text="Витрина пуста.")
        elif query_data == EDIT:
            query.delete_message()
            create_invoice(update, ctx, query.message.chat_id)
    except BadRequest:
        pass


def create_invoice(update: Update, ctx: CallbackContext, invoice_data, chat_id=None) -> None:
    """Sends an invoice"""
    if chat_id is None:
        chat_id = update.message.chat_id
    title = invoice_data['title']
    description = invoice_data['description']

    payload = invoice_data['payload']
    provider_token = environ.get('BOT_PAYMENT_TOKEN')
    currency = "RUB"
    price = invoice_data['price']
    prices = [LabeledPrice(title, price * 100)]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    ctx.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        provider_token,
        currency,
        prices,
        need_name=True,
        need_phone_number=True
    )


def precheckout_callback(update: Update, ctx: CallbackContext) -> None:
    query = update.pre_checkout_query
    # if query.invoice_payload != "Оплата через бота №XXX":
    #     query.answer(ok=False, error_message="Кажется, что-то пошло не так...")
    #     update.message.reply_text("Возникла ошибка при выполнении платежа.\n"
    #                               "Техническая поддержка: +79123456789")
    # else:
    query.answer(ok=True)


def successful_payment_callback(update: Update, ctx: CallbackContext) -> None:
    update.message.reply_text("Благодарим за покупку!")


def payment_connect(updater: Updater) -> None:
    """Adds required handlers"""
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("buy", create_invoice))
    dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dispatcher.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))


def pay_carousel_connect(updater: Updater) -> None:
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("carousel", show_carousel))
    dispatcher.add_handler(CallbackQueryHandler(callback=keyboard_callback_handler, pass_chat_data=True))


def carousel_editor_welcome(update: Update, ctx: CallbackContext):
    ctx.bot.send_message(chat_id=update.message.chat_id, text="Добро пожаловать в редактор витрины Вашего магазина!\n\n"
                                                              "Выберите один из вариантов ниже.",
                         reply_markup=ReplyKeyboardMarkup(INVOICE_EDITOR_KEYBOARD,
                                                          resize_keyboard=True))
    return 'test'


def invoice_editor_message_handler(update: Update, ctx: CallbackContext):
    msg = update.message.text
    chat_id = update.message.chat_id

    if ctx.user_data["is_admin"]:
        if msg == "Просмотр позиций (в режиме редактора)":
            ctx.bot.send_message(chat_id=chat_id, text="Просмотр позиций (в режиме редактора)")
            return 'test'
        if msg == "Добавление позиции":
            ctx.bot.send_message(chat_id=chat_id, text="Добавление позиции")
        if msg == "Изменение позиции":
            ctx.bot.send_message(chat_id=chat_id, text="Редактирование позиции")
        if msg == "Удаление позиции":
            ctx.bot.send_message(chat_id=chat_id, text="Удаление позиции")


def main() -> None:
    updater = Updater(environ.get('BOT_TOKEN'))
    updater.dispatcher.add_handler(CommandHandler("start", start))
    payment_connect(updater)
    pay_carousel_connect(updater)
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
