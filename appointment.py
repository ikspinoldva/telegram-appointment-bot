import datetime
import re
from collections import OrderedDict

import pytz

from typing import List, NamedTuple, Optional

import db
import exceptions


class Message(NamedTuple):
    """Structure of the parsed message about the new expense"""
    date: str
    sessions: list


class DayFormat(NamedTuple):
    """Structure of the day_format function"""
    date: str
    day_of_week: str


class Timeline(NamedTuple):
    """Structure of new sessions added to the db"""
    session_date: datetime.date
    session_time: str
    available: bool
    raw_text: str
    session_times: list


class DaysPlan(NamedTuple):
    """Structure of the timeline for issuing to the admin"""
    days: tuple
    days_times: dict


def add_sessions(raw_message: str):
    """Adds sessions.
    Takes as input the text of the message that came to the bot."""
    parsed_message = _parse_message(raw_message)
    session_date = parsed_message.date
    session_times = parsed_message.sessions

    for session in session_times:
        if len(session) in (1, 2):
            time_session = datetime.time(int(session), 0, 0)
        elif ':' in session:
            session = session.split(':')
            time_session = datetime.time(int(session[0]), int(session[1]), 0)
        inserted_row_id = db.insert({
            "session_date": str(session_date),
            "session_time": str(time_session),
            "available": True,
            "raw_text": raw_message,
            "created": _get_now_formatted()
        })

    return Timeline(
                    session_date=session_date,
                    session_time=str(time_session),
                    available=True,
                    raw_text=raw_message,
                    session_times=session_times
                    )


def _parse_message(raw_message: str):
    """Parses the text of incoming messages about new sessions."""
    regexp_result = re.match(
        r"(\d{2}\.\d{2})\s+((?:\d{2}:\d{2} |\d:\d{2} |\d:\d{2}|\d{2}:\d{2}|\d{2} |\d{2}|\d |\d)+)",
        raw_message.strip()
    )

    if not regexp_result or not regexp_result.group(0) or not regexp_result.group(1) \
            or not regexp_result.group(2):
        raise exceptions.NotCorrectMessage(
            "I can't understand the message. Write a message in the format, "
            "for example:\n05.04 10 12 13:30"
            "\nWhere 05.04 is the date, then the time of the sessions, "
            "separated by a space.")

    session_date = regexp_result.group(1).split('.')
    session_times = regexp_result.group(2).split(' ')
    now_date = str(get_now_datetime()).split()[0].split('-')
    try:
        day_session = datetime.date(int(get_now_datetime().year),
                                    int(session_date[1]),
                                    int(session_date[0]))
    except ValueError:
        raise exceptions.NotCorrectMessage(
            'Wrong date or time\nWrite a message in the format:'
            '\n<i>05.04 10 12 13:30</i>\nWhere 05.04 is the date, '
            'then the time of the sessions, separated by a space.'
        )
    for time in session_times:
        if len(time) in (1, 2):
            if int(time) > 23 or int(time) < 0:
                raise exceptions.NotCorrectMessage(
                    'Wrong date or time\nWrite a message in the format:'
                    '\n<i>05.04 10 12 13:30</i>\nWhere 05.04 is the date, '
                    'then the time of the sessions, separated by a space.'
                )
        else:
            if ':' not in time:
                raise exceptions.NotCorrectMessage(
                    'Wrong date or time\nWrite a message in the format:'
                    '\n<i>05.04 10 12 13:30</i>\nWhere 05.04 is the date, '
                    'then the time of the sessions, separated by a space.'
                )
            hours = time.split(':')[0]
            minutes = time.split(':')[1]
            if int(hours) < 0 or int(hours) > 23 \
                    or int(minutes) < 0 or int(minutes) > 59:
                raise exceptions.NotCorrectMessage(
                    'Wrong date or time\nWrite a message in the format:'
                    '\n<i>05.04 10 12 13:30</i>\nWhere 05.04 is the date, '
                    'then the time of the sessions, separated by a space.'
                )

    delta = day_session - datetime.date(int(now_date[0]), int(now_date[1]), int(now_date[2]))
    if delta.days >= 0:
        session_date.append(str(get_now_datetime().year))

    elif delta.days < 0:
        session_date.append(str(int(get_now_datetime().year) + 1))

    session_date = datetime.date(int(session_date[2]), int(session_date[1]), int(session_date[0]))
    return Message(date=session_date, sessions=session_times)


def create_sessions(raw_text) -> str:
    try:
        session = add_sessions(raw_text)
    except exceptions.NotCorrectMessage as e:
        message_answer = str(e)
        return message_answer
    about_day = day_format(str(session.session_date))
    message_answer = \
        f'For {about_day.day_of_week} <b>{about_day.date}</b> ' \
        f'the sessions are open at hours: {session.session_times}'
    return message_answer


def get_all_sessions():
    cursor = db.get_cursor()
    cursor.execute("SELECT session_date, id, available, session_time, "
                   "customer_name, customer_username, updated, customer_user_id "
                   "FROM timeline "
                   "ORDER BY session_date, session_time ")
    result = cursor.fetchall()
    if not result:
        return False
    result_dict = OrderedDict()
    for session in result:
        if session[2] == 1:
            if session[0] not in result_dict:
                result_dict[session[0]] = [(session[1], '✔️',
                                           session[3], '',
                                           '', '', '')]
            else:
                result_dict[session[0]].append((session[1], '✔️',
                                                session[3], '',
                                                '', '', ''))
        elif session[2] == 0:
            if session[0] not in result_dict:
                result_dict[session[0]] = [(session[1], '✖️',
                                           session[3], session[4],
                                           f"@{session[5]}", session[6], session[7])]
            else:
                result_dict[session[0]].append((session[1], '✖️',
                                                session[3], session[4],
                                                f"@{session[5]}", session[6], session[7]))

    return result_dict


def get_timeline() -> str:
    """Returns the timeline in string format for view in bot"""
    sessions = get_all_sessions()
    if sessions:
        message_answer = ''
        for day, times in sessions.items():
            about_day = day_format(day)
            message_answer += \
                f'\n\n{about_day.day_of_week} <b>{about_day.date}</b>\n\n'
            for time in times:
                message_answer += \
                    f'{time[1]} {time[2][:5]} {time[3]} {time[4]} {time[5][5:-3]}\n'
                # available, session_time, customer_name, customer_username, updated
    else:
        message_answer = \
            'Timeline is empty 👾'
    return message_answer


def day_format(day: str):
    date_day = day.split('-')
    date_day = datetime.date(int(date_day[0]), int(date_day[1]), int(date_day[2]))
    view_date = date_day.strftime("%d.%m.%Y")
    day_of_week = date_day.strftime("%A")
    return DayFormat(date=view_date, day_of_week=day_of_week)


def delete_session(session_id: int) -> None:
    db.delete_session(session_id)


def delete_day(day: str) -> None:
    db.delete_day(day)


def change_info(raw_message: str) -> None:
    parsed_message = _parse_message_info(raw_message)
    db.update_info(parsed_message)


def _parse_message_info(raw_message: str) -> str:
    split_message = raw_message.split()
    if len(split_message) < 2:
        raise exceptions.NotCorrectMessage('Incorrect message. '
                                           'Enter the word "info", then a space, '
                                           'whatever is written next will be added to '
                                           'the information about master.')
    result_message = ' '.join(split_message[1:])
    return result_message


def change_price(raw_message: str):
    parsed_message = _parse_message_price(raw_message)
    price1, price2, price3 = parsed_message
    db.update_price(price1, price2, price3)


def _parse_message_price(raw_message: str) -> tuple:
    regexp_result = re.match(r"[Pp]rice \d+ \d+ \d+", raw_message)
    if not regexp_result or not regexp_result.group(0):
        raise exceptions.NotCorrectMessage(
            "Incorrect message. Enter the word 'price' "
            "followed by a space, then price 1, price 2, "
            "and price 3 separated by a space, for example: price 99 99 99")
    price1, price2, price3 = regexp_result.group(0).split()[1:]
    result = (price1, price2, price3)
    return result

def change_address(raw_message: str) -> None:
    parsed_message = _parse_message_address(raw_message)
    db.update_address(parsed_message)


def _parse_message_address(raw_message: str) -> str:
    split_message = raw_message.split()
    if len(split_message) < 2:
        raise exceptions.NotCorrectMessage('Incorrect message. '
                                           'Enter the word "local", then a space, '
                                           'whatever is written next will be added to '
                                           'the address.')

    result_message = ' '.join(split_message[1:])
    return result_message

def get_available_sessions():
    cursor = db.get_cursor()
    cursor.execute("SELECT session_date, session_time, id "
                   f"FROM timeline WHERE available={True} ORDER BY session_date, session_time")
    result = cursor.fetchall()
    if not result:
        return False
    result_dict = OrderedDict()
    for session in result:
        if session[0] not in result_dict:
            result_dict[session[0]] = [(session[1], session[2])]
        else:
            result_dict[session[0]].append((session[1], session[2]))
    return result_dict


def get_about() -> str:
    cursor = db.get_cursor()
    cursor.execute("SELECT about_master FROM about")
    result = cursor.fetchone()[0]
    return result


def get_address() -> str:
    cursor = db.get_cursor()
    cursor.execute("SELECT raw_address FROM about")
    result = cursor.fetchone()[0]
    return result


def get_price() -> tuple:
    cursor = db.get_cursor()
    cursor.execute("SELECT price1, price2, price3 FROM about")
    return cursor.fetchone()


def booking_session(session_id: int, user_id: int,
                    username: str, user_fullname: str) -> None:
    db.booking(session_id, user_id, username,
               user_fullname, _get_now_formatted())


def cancel_session(session_id: int) -> None:
    db.reset_session(session_id)


def check_client_in_db(user_id: int):
    cursor = db.get_cursor()
    cursor.execute(f"SELECT id, session_date, session_time "
                   f"FROM timeline "
                   f"WHERE customer_user_id={user_id}")
    result = cursor.fetchall()
    if result:
        return result[0]
    return False


def get_booked_sessions():
    cursor = db.get_cursor()
    cursor.execute(f"SELECT id, session_date, "
                   f"session_time, customer_user_id, "
                   f"customer_username "
                   f"FROM timeline WHERE available={False} "
                   f"ORDER BY session_date, session_time")
    result = cursor.fetchall()
    if not result:
        return False
    result_dict = OrderedDict()
    for session in result:
        if session[1] not in result_dict:
            result_dict[session[1]] = [(session[0], session[2], session[3], session[4])]
        else:
            result_dict[session[1]].append((session[0], session[2], session[3], session[4]))
    return result_dict


def _get_now_formatted() -> str:
    """Returns today date in str format"""
    return get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def get_now_datetime() -> datetime.datetime:
    """Returns today datetime with Warsaw timezone."""
    tz = pytz.timezone("Europe/Warsaw")
    now = datetime.datetime.now(tz)
    return now


def refresh_db() -> None:
    sessions = get_all_sessions()
    if sessions:
        for day, times in sessions.items():
            day_split = day.split('-')
            year, month, day = int(day_split[0]), int(day_split[1]), int(day_split[2])
            for time in times:
                session_id = int(time[0])
                time_split = time[2].split(':')
                hours, minutes, seconds = int(time_split[0]), int(time_split[1]), int(time_split[2])
                session_datetime = datetime.datetime(year, month, day, hours, minutes, seconds)
                delta = session_datetime - datetime.datetime.now()
                if delta.days < 0:
                    delete_session(session_id)

