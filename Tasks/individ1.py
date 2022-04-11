#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Для своего варианта лабораторной работы 2.17 необходимо
реализовать хранение данных в базе данных SQLite3.
"""

import argparse
import sqlite3
import typing as t
from pathlib import Path


def add_human(
        database_path: Path,
        name: str,
        zodiac: str,
        year: str
) -> None:
    """
    Человека в базу данных
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    # Получить идентификатор пути в базе данных.
    # Если такой записи нет, то добавить информацию о новом маршруте.
    cursor.execute(
        """
        SELECT human_id FROM humans WHERE name = ?
        """,
        (name,)
    )
    row = cursor.fetchone()
    if row is None:
        cursor.execute(
            """
            INSERT INTO humans (name) VALUES (?)
            """,
            (name,)
        )
        human_id = cursor.lastrowid
    else:
        human_id = row[0]

        # Добавить информацию о новом продукте.
    cursor.execute(
        """
        INSERT INTO way (zodiac, human_id, year)
        VALUES (?, ?, ?)
        """,
        (zodiac, human_id, year)
    )
    conn.commit()
    conn.close()


def select_all(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать всех людей
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT people.zodiac, humans.name, people.year
        FROM people
        INNER JOIN humans ON humans.human_id = people.human_id
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "zodiac": row[0],
            "name": row[1],
            "year": row[2],
        }
        for row in rows
    ]


def select_name(
        database_path: Path, name1: str
) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать человека по фамилии
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT people.zodiac, humans.name, people.year
        FROM people
        INNER JOIN humans ON humans.human_id = people.human_id
        WHERE humans.name == ?
        """,
        (name1,)
    )
    # datetime
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "zodiac": row[0],
            "name": row[1],
            "year": row[2],
        }
        for row in rows
    ]


def display_people(people: t.List[t.Dict[str, t.Any]]) -> None:
    """
    Отобразить список людей
    """
    if people:
        line = '+-{}-+-{}-+-{}-+'.format(
            '-' * 30,
            '-' * 20,
            '-' * 20
        )
        print(line)
        print(
            '| {:^30} | {:^20} | {:^20} |'.format(
                "Ф.И.О.",
                "Знак зодиака",
                "Дата рождения"
            )
        )
        print(line)

        for human in people:
            print(
                '| {:<30} | {:>20} | {:<20} |'.format(
                    human.get('name', ''),
                    human.get('zodiac', ''),
                    human.get('year', '')
                )
            )
        print(line)

    else:
        print("Человек не найден")


def create_db(database_path: Path) -> None:
    """
    Создать базу данных
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    # Создать таблицу людей по фамилиям
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS humans (
        human_id INTEGER PRIMARY KEY AUTOINCREMENT,
        destination TEXT NOT NULL
        )
        """
    )
    # Создать таблицу людей с полной информацией
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS people (
        people_id INTEGER PRIMARY KEY AUTOINCREMENT,
        zodiac INTEGER NOT NULL,
        human_id INTEGER NOT NULL,
        year TEXT NOT NULL,
        FOREIGN KEY(human_id) REFERENCES humans(human_id)
        )
        """
    )
    conn.close()


def main(command_line=None):
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.home() / "people.db"),
        help="The database file name"
    )
    # Создать основной парсер командной строки
    parser = argparse.ArgumentParser("humans")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    # Создать субпарсер для добавления человека
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new human"
    )
    add.add_argument(
        "-z",
        "--zodiac",
        action="store",
        required=True,
        help="The human's zodiac"
    )
    add.add_argument(
        "-n",
        "--name",
        action="store",
        required=True,
        help="The human's name"
    )
    add.add_argument(
        "-yr",
        "--year",
        action="store",
        required=True,
        help="The human's year"
    )
    # Создать субпарсер для отображения всех людей
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all people"
    )
    # Создать субпарсер для выбора человека
    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
        help="Select the human"
    )
    select.add_argument(
        "-n",
        "--name",
        action="store",
        required=True,
        help="The required human"
    )
    args = parser.parse_args(command_line)
    db_path = Path(args.db)
    create_db(db_path)
    if args.command == "add":
        add_human(db_path, args.zodiac, args.name, args.year)
    elif args.command == "display":
        display_people(select_all(db_path))
    elif args.command == "select":
        display_people(select_name(db_path, args.name))
    pass


if __name__ == '__main__':
    main()