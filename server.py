"""Controller file"""

import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime

import appointment
import exceptions

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def access_id(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return True
    return False


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if access_id(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        item1 = types.KeyboardButton('/timeline')
        item2 = types.KeyboardButton('/delete')
        markup.add(item1, item2)
        await message.answer("Hi, admin! Im bot for appointment!\n"
                             "You can enter session dates and times "
                             "into the bot, and it will help you book people. "
                             "You can also make your own reservations through "
                             "the bot, it's convenient to keep everything in one "
                             "database, detailed instructions on the bot in the /help "
                             "command", reply_markup=markup)
    else:
        await message.answer("Hi! Im bot for appointment!\n"
                             "Use the commands on the menu to book a session. "
                             "Then you can cancel the session through the bot, "
                             "and the master will be notified. You can see the prices, "
                             "the address and the info about the master through this bot, "
                             "isn't it great? :)\nWelcome!")


@dp.message_handler(commands=['help'])
async def helper(message: types.Message):
    if access_id(message.from_user.id):
        await message.answer('Commands:'
                             '\n\n/book_session - Displays a list of available sessions; '
                             'by selecting one, you book that session. The wizard receives '
                             'a notification of your appointment, your name on the Telegram, '
                             'and a link to your profile to contact you. You can only book for 1 '
                             'session from your account. If you need more, contact the wizard '
                             'directly @masterslink'
                             '\nThe wizard has the ability to book as many sessions as he wants '
                             'on his own behalf. In that case, no one will be notified.'
                             "\n\n/cancel_session - A list of booked sessions for cancellation "
                             "is displayed. After selecting a session, the client's session is "
                             "canceled and the session is available for booking again. The "
                             "client receives a notification of the session cancellation."
                             '\n\n/price - Shows a list of prices for the services '
                             'of this wizard'
                             '\n\n/address - Shows the address where the wizard performs '
                             'his services'
                             '\n\n/about - Shows information about wizard. '
                             '\n\nThe bot sends the client two reminders: about a day before the '
                             'session and a few hours before.')
        await message.answer("Admin commands:"
                             "\n\n/timeline - Displays a list of all open sessions. Booked and "
                             "available. The first character indicates that the session is "
                             "available. Next is the session time. If the session is booked, "
                             "it is followed by the client's name, a link to their profile, "
                             "and the reservation time."
                             "\n\n/delete - Displays a list of all sessions for deletion. "
                             "Clicking on a session deletes it. You can also delete an entire "
                             "day with the corresponding button. If the session has been booked, "
                             "the client will receive a notification to cancel the session. "
                             "\n\n\nAdding new sessions - You must enter the date and the list "
                             "of sessions in the format: 12.05 8 9:30 12 14:30 16, where 12.05 - "
                             "date, and then the time of the sessions, separated by a space. After "
                             "sending to the bot, these sessions will be available for booking."
                             "\n\nPrice update - You need to enter the keyword 'price', and then "
                             "after the space 3 prices, in the format: price 99 55 33. Where "
                             "service 1 - 99, service 2 - 55, service 3 - 33. The number of prices "
                             "can be different, if necessary. After sending a message to the bot, "
                             "prices go to the database, from which they are issued to users."
                             "\n\nAddress update - It is necessary to enter the keyword 'local' "
                             "followed by a space in the format:  local Śląska 11, Gdynia. "
                             "Everything that comes after the space writes into the address. After "
                             "sending the message to the bot, the address is updated."
                             "\n\nUpdate information about wizard - You must enter the keyword "
                             "'info' followed by a space in the format: info I have been cutting "
                             "hair for 3 years. Anything that comes after the space is written in "
                             "the information about the wizard. After sending a message to the bot "
                             "the information about the wizard is updated.")
    else:
        await message.answer('Commands:'
                             '\n\n/book_session - Displays a list of available sessions; '
                             'by selecting one, you book that session. The wizard receives '
                             'a notification of your appointment, your name on the Telegram, '
                             'and a link to your profile to contact you. You can only book for 1 '
                             'session from your account. If you need more, contact the wizard '
                             'directly @masterslink'
                             '\n\n/cancel_session - If you are booked for a session but want to '
                             'cancel - send the bot this command, it will send you a button to '
                             'confirm the cancellation of the session. After canceling the '
                             'session, you will be able to book the session again, the wizard '
                             'will receive a notification of your cancellation.'
                             '\n\n/price - Shows a list of prices for the services '
                             'of this wizard'
                             '\n\n/address - Shows the address where the wizard performs '
                             'his services'
                             '\n\n/about - Shows information about wizard. '
                             '\n\nThe bot sends the client two reminders: about a day before the '
                             'session and a few hours before.')


@dp.message_handler(commands=['about'])
async def get_about_master(message: types.Message):
    await message.answer(appointment.get_about())


@dp.message_handler(commands=['address'])
async def get_address(message: types.Message):
    await message.answer(appointment.get_address())


@dp.message_handler(commands=['price'])
async def get_price(message: types.Message):
    price1, price2, price3 = appointment.get_price()
    message_answer = f"<b>- PRICE LIST -</b>\n" \
                     f"\n- Price 1: <b>{price1}</b> PLN" \
                     f"\n- Price 2: <b>{price2}</b> PLN" \
                     f"\n- Price 3: <b>{price3}</b> PLN"
    await message.answer(message_answer, parse_mode='html')


@dp.message_handler(commands=['timeline'])
async def view_timeline(message: types.Message):
    """Only for admin"""
    if access_id(message.from_user.id):
        await message.answer(appointment.get_timeline(), parse_mode='html')
    else:
        await message.answer('<b>Unknown command</b>', parse_mode='html')


@dp.message_handler(commands=['delete'])
async def del_from_timeline(message: types.Message):
    """Only for admin"""
    if access_id(message.from_user.id):
        markup = types.InlineKeyboardMarkup(row_width=2)
        sessions = appointment.get_all_sessions()
        if sessions:
            await message.answer("Choose a session to remove:", parse_mode='html')
            markup_rows = 2
            for day, times in sessions.items():
                buttons_added = []
                users_id = ''
                for time in times:
                    # id, available, session_time, customer_name, customer_username,
                    # updated, customer_user_id
                    if time[1] == '✖️':
                        users_id += f'{time[6]} '
                    item = types.InlineKeyboardButton(f'{time[2][:5]} {time[1]}',
                                                      callback_data=
                                                      f'{time[0]} {day} {time[2][:5]} '
                                                      f'{time[6]} {time[4]} del')

                    buttons_added.append(item)
                    if len(buttons_added) == markup_rows:
                        markup.add(*buttons_added)
                        buttons_added = []
                if buttons_added:
                    markup.add(buttons_added[0])
                item = types.InlineKeyboardButton('Delete all day',
                                                  callback_data=f'{str(day)} {users_id} del_all')
                markup.add(item)
                about_day = appointment.day_format(day)
                message_answer = f'{about_day.day_of_week} <b>{about_day.date}</b>'
                await message.answer(message_answer, reply_markup=markup, parse_mode='html')
                markup = types.InlineKeyboardMarkup(row_width=2)
        else:
            await message.answer('Timeline is empty')

    else:
        await message.answer('<b>Unknown command</b>', parse_mode='html')


@dp.message_handler(commands=['book_session'])
async def book_session(message):
    appointment.refresh_db()
    if message.from_user.username is not None:
        user_fullname = message.from_user.first_name
        if message.from_user.last_name:
            user_fullname += f'-{message.from_user.last_name}'
        markup_rows = 2
        sessions = appointment.get_available_sessions()
        if sessions:
            markup = types.InlineKeyboardMarkup(row_width=2)
            await message.answer('Choose a session:')
            for day, times in sessions.items():
                buttons_added = []
                about_day = appointment.day_format(day)
                # time, id
                for time in times:
                    item = types.InlineKeyboardButton(f'{time[0][:5]}',
                                                      callback_data=f'{time[1]} '
                                                                    f'{user_fullname} {day} {time[0]} book')
                    buttons_added.append(item)
                    if len(buttons_added) == markup_rows:
                        markup.add(*buttons_added)
                        buttons_added = []
                if buttons_added:
                    markup.add(buttons_added[0])
                message_answer = f'{about_day.day_of_week} {about_day.date}'
                await message.answer(message_answer, reply_markup=markup)
                markup = types.InlineKeyboardMarkup(row_width=2)
        else:
            await message.answer('No sessions available')
    else:
        await message.answer("❗️You can't book a session because you don't have a username. "
                             "Get a username so that we can give the master a link to your "
                             "account, and then come back :)")


@dp.message_handler(commands=['cancel_session'])
async def cancel_session(message):
    if access_id(message.from_user.id):
        sessions = appointment.get_booked_sessions()
        markup = types.InlineKeyboardMarkup(row_width=1)
        if sessions:
            await message.answer('Choose a session to cancel:')
            # session_id, time, user_id, username
            for day, times in sessions.items():
                about_day = appointment.day_format(day)
                for time in times:
                    item = types.InlineKeyboardButton(
                        f"{time[1][:5]} @{time[3]}",
                        callback_data=f"{time[0]} {day} {time[1][:5]} "
                                      f"{time[2]} {time[3]} cancel")
                    markup.add(item)
                message_answer = f"{about_day.day_of_week} {about_day.date}"
                await message.answer(message_answer, reply_markup=markup)
                markup = types.InlineKeyboardMarkup(row_width=1)

        else:
            await message.answer('No booked sessions')
    else:
        session = appointment.check_client_in_db(message.from_user.id)
        if session:
            markup = types.InlineKeyboardMarkup(row_width=1)
            session_id, day, session_time = session
            about_day = appointment.day_format(day)
            item = types.InlineKeyboardButton("Confirm canceling",
                                              callback_data=f"{session_id} "
                                                            f"{day} {session_time[:5]} "
                                                            f"cancel")
            markup.add(item)
            message_answer = \
                f"Confirm session cancellation for " \
                f"{about_day.day_of_week}, " \
                f"{about_day.date} at {session_time[:5]}"
            await message.answer(message_answer, reply_markup=markup)
            markup = types.ReplyKeyboardMarkup(row_width=1)
        else:
            await message.answer('No session booked')


@dp.message_handler(content_types=['text'])
async def text_reader(message):
    if access_id(message.from_user.id):
        text_input = message.text.lower()
        if text_input.startswith('price'):
            try:
                appointment.change_price(message.text)
                await message.answer('Ok, changes applied.')
            except exceptions.NotCorrectMessage as e:
                await message.answer(str(e))

        elif text_input.startswith('local'):
            try:
                appointment.change_address(message.text)
                await message.answer('Ok, changes applied.')
            except exceptions.NotCorrectMessage as e:
                await message.answer(str(e))

        elif text_input.startswith('info'):
            try:
                appointment.change_info(message.text)
                await message.answer('Ok, changes applied.')
            except exceptions.NotCorrectMessage as e:
                await message.answer(str(e))
        else:
            await message.answer(appointment.create_sessions(text_input), parse_mode='html')
    else:
        await message.answer('<b>Unknown command</b>', parse_mode='html')


@dp.callback_query_handler(lambda call: True)
async def callback_inline(call):
    try:
        if call.message:
            if call.data.endswith('del'):
                session_id, day, time = call.data.split()[:3]
                about_day = appointment.day_format(day)
                if len(call.data.split()) == 6:

                    user_id, username = call.data.split()[3:5]
                    if int(user_id) != ADMIN_ID:
                        await bot.send_message(call.from_user.id,
                                               f"@{username} session for "
                                               f"{about_day.day_of_week}, "
                                               f"{about_day.date} at {time} "
                                               f"is cancelled, notice was sent.")
                        try:
                            await bot.send_message(int(user_id), f'Your session for '
                                                                 f'{about_day.day_of_week}, '
                                                                 f'{about_day.date} at {time} '
                                                                 f'has been deleted by the admin, '
                                                                 f'you can contact the master for '
                                                                 f'details:\n@masterslink')
                        except Exception:
                            print('Error send message to user about delete a him session')

                session_id = int(session_id)
                appointment.delete_session(session_id)
                await bot.send_message(call.from_user.id,
                                       f'Deleted session for {about_day.day_of_week}, '
                                       f'{about_day.date} at {time}')
            elif call.data.endswith('del_all'):
                day = call.data.split()[0]
                about_day = appointment.day_format(day)
                if len(call.data.split()) > 2:
                    users_id = call.data.split()[1:-1]
                    for user_id in users_id:
                        if int(user_id) != ADMIN_ID:
                            try:
                                await bot.send_message(int(user_id), f"Your session for "
                                                                     f"{about_day.day_of_week}, "
                                                                     f"{about_day.date} has been "
                                                                     f"deleted by the admin, you "
                                                                     f"can contact the master "
                                                                     f"for details:\n@masterslink")
                            except Exception:
                                print(f'Error send message to user {users_id} '
                                      f'about delete him session day')
                appointment.delete_day(day)

                await bot.send_message(call.from_user.id,
                                       f'Deleted all sessions for {about_day.day_of_week}, '
                                       f'{about_day.date}')
            elif call.data.endswith('book'):
                session_id, user_fullname, day, time = call.data.split()[:4]
                about_day, address = appointment.day_format(day), appointment.get_address()
                if access_id(call.from_user.id):
                    appointment.booking_session(int(session_id), int(call.from_user.id),
                                                call.from_user.username, user_fullname)
                    await bot.send_message(call.from_user.id,
                                           f'Reservations for {about_day.day_of_week}, '
                                           f'{about_day.date} at {time[:5]}')
                else:
                    session = appointment.check_client_in_db(int(call.from_user.id))
                    # id date time
                    if session:
                        user_session_date = session[1]
                        about_day = appointment.day_format(str(user_session_date))
                        user_session_time = session[2]
                        await bot.edit_message_text(chat_id=call.from_user.id,
                                                    message_id=call.message.message_id,
                                                    text=f"You are already booked for "
                                                         f"{about_day.day_of_week}, "
                                                         f"{about_day.date} at {user_session_time[:5]}. "
                                                         f"To change your session, first cancel "
                                                         f"the existing.",
                                                    reply_markup=None)
                    else:
                        appointment.booking_session(int(session_id), int(call.from_user.id),
                                                    call.from_user.username, user_fullname)
                        await bot.edit_message_text(chat_id=call.from_user.id,
                                                    message_id=call.message.message_id,
                                                    text=f"Reservations for "
                                                         f"{about_day.day_of_week}, "
                                                         f"{about_day.date} at "
                                                         f"{time[:5]}"
                                                         f"\nName: {user_fullname}"
                                                         f"\nAcc: @{call.from_user.username}"
                                                         f"\nAddress: {address}\n"
                                                         f"\nSee you :)",
                                                    reply_markup=None)
                        try:
                            await bot.send_message(ADMIN_ID, f'{user_fullname} '
                                                         f'booked for {about_day.day_of_week}, '
                                                         f'{about_day.date} at {time[0:5]}\n'
                                                         f'Acc: @{call.from_user.username}')
                        except Exception:
                            print('Error send message to Admin about booking session')
            elif call.data.endswith('cancel'):
                session_id, day, session_time = call.data.split()[:3]
                about_day = appointment.day_format(day)
                if access_id(call.from_user.id):
                    user_id, username = call.data.split()[3:5]
                    if int(user_id) != ADMIN_ID:
                        try:
                            await bot.send_message(int(user_id),
                                                   f"Your session on "
                                                   f"{about_day.day_of_week}, "
                                                   f"{about_day.date} at {session_time} "
                                                   f"was cancelled by the admin, please "
                                                   f"contact the master for details:"
                                                   f"\n@masterslink")
                        except Exception:
                            print('Error send message to user about canceled him session')

                    await bot.send_message(call.from_user.id,
                                           f"@{username}'s session on "
                                           f"{about_day.day_of_week}, "
                                           f"{about_day.date} at {session_time} "
                                           f"has been canceled")

                else:
                    try:
                        await bot.send_message(ADMIN_ID,
                                               f"@{call.from_user.username} "
                                               f"cancelled his session for "
                                               f"{about_day.day_of_week}, "
                                               f"{about_day.date} at {session_time}")
                    except Exception:
                        print('Error send message to admin about user canceling session')
                    await bot.edit_message_text(chat_id=call.from_user.id,
                                                message_id=call.message.message_id,
                                                text=f"Your session for "
                                                     f"{about_day.day_of_week}, "
                                                     f"{about_day.date} at "
                                                     f"{session_time} is cancelled",
                                                reply_markup=None)
                appointment.cancel_session(int(session_id))
                print(call.data.split())
    except Exception as e:
        print(repr(e))


async def user_reminder() -> None:
    while True:
        sessions = appointment.get_booked_sessions()
        now_datetime = datetime.now()
        if sessions:
            for day, times in sessions.items():
                day_split = day.split('-')
                year, month, day = int(day_split[0]), int(day_split[1]), int(day_split[2])
                for time in times:
                    user_id = int(time[2])
                    if user_id != ADMIN_ID:
                        time_split = time[1].split(':')
                        hours, minutes, seconds = int(time_split[0]), int(time_split[1]), int(time_split[2])
                        session_datetime = datetime(year, month, day, hours, minutes, seconds)
                        delta = session_datetime - now_datetime
                        if delta.days == 0:
                            hours_to_session = int(str(delta).split(':')[0])
                            if 21 <= hours_to_session <= 24:
                                await bot.send_message(user_id, f"Just a reminder about your "
                                                                f"session tomorrow at {time[1][:5]}")
                                print(f'Send message to {user_id} about 24')

                            elif 1 <= hours_to_session <= 4:
                                await bot.send_message(user_id, f"I'll wait for you at {time[1][:5]}, "
                                                                f"tell me if you're going to be late.")
                                print(f'Send message to {user_id} about 3')
        await asyncio.sleep(9300)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(user_reminder())
    executor.start_polling(dp, skip_updates=True)





