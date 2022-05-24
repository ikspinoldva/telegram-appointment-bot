import os
from typing import Dict, List, Tuple

import sqlite3

conn = sqlite3.connect(os.path.join("db", "appointment.db"))
cursor = conn.cursor()


def insert(column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(
        f"INSERT INTO timeline "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def update_info(info: str):
    cursor.execute(
        f'UPDATE about SET about_master="{info}"')
    conn.commit()


def update_address(address_text: str):
    cursor.execute(
        f'UPDATE about SET raw_address="{address_text}"')
    conn.commit()


def update_price(price1, price2, price3) -> None:
    cursor.execute(
        f'UPDATE about SET price1="{price1}", price2="{price2}", price3="{price3}" ')
    conn.commit()


def delete_session(session_id: int) -> None:
    cursor.execute(f"DELETE FROM timeline WHERE id={session_id}")
    conn.commit()


def delete_day(day: str) -> None:
    cursor.execute(f"DELETE FROM timeline WHERE date(session_date)='{day}'")
    conn.commit()


def booking(session_id: int, user_id: int, username: str,
            user_fullname: str, booking_time: str) -> None:
    cursor.execute(f'UPDATE timeline SET customer_user_id={user_id}, '
                   f'customer_username="{username}", '
                   f'customer_name="{user_fullname}", '
                   f'available={False}, '
                   f'updated="{booking_time}" '
                   f'WHERE id={session_id}')
    conn.commit()


def reset_session(session_id: int) -> None:
    cursor.execute(f"UPDATE timeline SET "
                   f"customer_user_id=NULL, "
                   f"customer_username=NULL, "
                   f"customer_name=NULL, "
                   f"available={True}, "
                   f"updated=NULL "
                   f"WHERE id={session_id}")
    conn.commit()




def get_cursor():
    return cursor


def _init_db():
    """init db"""
    with open("createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """Checks if the database is initialized, if not - initializes"""
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='timeline' OR type='table' AND name='about'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()
