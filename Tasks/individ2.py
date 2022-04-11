#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Самостоятельно изучите работу с пакетом python-psycopg2 для работы с базами данных
PostgreSQL. Для своего варианта лабораторной работы 2.17 необходимо реализовать
возможность хранения данных в базе данных СУБД PostgreSQL.
"""

import psycopg2
import typing as t
import argparse


def connect():
    conn = psycopg2.connect(
        user="postgres",
        password="Pa$$w0rd",
        host="127.0.0.1",
        port="5432",
        database="postgres"
    )

    return conn


def add_human(
        name: str,
        zodiac: str,
        year: str
) -> None:
    cursor = connect().cursor()
    # Получить идентификатор человека в базе данных
    # Если такой записи нет, то добавить информацию о человеке
    cursor.execute(
        """
        SELECT human_id FROM human WHERE name = %s;
        """,
        (name,)
    )
    row = cursor.fetchone()
    if row is None:

        cursor.execute(
            """
            INSERT INTO human (name) VALUES (%s)
            """,
            (name,)
        )
        human_id = cursor.lastrowid
    else:
        human_id = row[0]

        # Добавить информацию о новом продукте.
    cursor.execute(
        """
        INSERT INTO people (human_id, zodiac, year)
        VALUES (%s, %s, %s)
        """,
        (human_id, zodiac, year)
    )
    connect().commit()


def select_people():
    """
    Выбрать всех людей
    """
    cursor = connect().cursor()
    cursor.execute(
        """
        SELECT human.name, people.zodiac, people.year
        FROM people
        INNER JOIN human ON human.human_id = people.human_id
        """
    )
    rows = cursor.fetchall()
    connect().close()
    return [
        {
            "name": row[0],
            "zodiac": row[1],
            "year": row[2],

        }
        for row in rows
    ]


def select_human(name) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать человека по фамилии
    """
    cursor = connect().cursor()
    cursor.execute(
        """
        SELECT human.name, people.zodiac, people.year
        FROM people
        INNER JOIN human ON human_name.human_id = people.human_id
        WHERE human_name.name = %s
        """,
        (name,)
    )
    rows = cursor.fetchall()
    connect().close()
    return [
        {
            "name": row[0],
            "zodiac": row[1],
            "year": row[2],
        }
        for row in rows
    ]


def display(people: t.List[t.Dict[str, t.Any]]) -> None:
    """
    Отобразить список людей
    """
    if people:
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 20,
            '-' * 20
        )
        print(line)
        print(
            '| {:^4} | {:^30} | {:^20} | {:^20} |'.format(
                "No",
                "ФИО",
                "Знак зодиака",
                "Дата рождения"
            )
        )
        print(line)
        for idx, human in enumerate(people, 1):
            print(
                '| {:>4} | {:<30} | {:<20} | {:>20} |'.format(
                    idx,
                    human.get('name', ''),
                    human.get('zodiac', ''),
                    human.get('year', 0)

                )
            )
            print(line)
        else:
            print("Список пуст")


def create_db() -> None:
    """
    Создать базу данных.
    """
    cursor = connect().cursor()
    # Создать таблицу людей с ФИО
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS human (
        human_id serial,
        PRIMARY KEY(human_id),
        name TEXT NOT NULL
        )
        """
    )
    # Создать таблицу с полной информацией о людях
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS people (
        human_id serial,
        PRIMARY KEY(human_id),
        zodiac INTEGER NOT NULL,
        year TEXT NOT NULL,
        FOREIGN KEY(human_id) REFERENCES human(human_id)
        ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )


def main(command_line=None):
    parser = argparse.ArgumentParser("people")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    subparsers = parser.add_subparsers(dest="command")

    # Создать субпарсер для добавления человека
    add = subparsers.add_parser(
        "add",
        help="Add a new human"
    )
    add.add_argument(
        "-n",
        "--name",
        action="store",
        required=True,
        help="The human's name"
    )
    add.add_argument(
        "-z",
        "--zodiac",
        action="store",
        required=True,
        help="The human's zodiac"
    )
    add.add_argument(
        "-yr",
        "--year",
        action="store",
        required=True,
        help="The human's year"
    )
    _ = subparsers.add_parser(
        "display",
        help="Display all people"
    )
    # Создать субпарсер для выбора человека
    select = subparsers.add_parser(
        "select",
        help="Select the human"
    )
    select.add_argument(
        "-s",
        "--select",
        action="store",
        required=True,
        help="The human's name"
    )
    args = parser.parse_args(command_line)
    create_db()
    if args.command == "add":
        add_human(args.name, args.zodiac, args.year)
    elif args.command == "select":
        display(select_human(args.name))
    elif args.command == "display":
        display(select_people())
    pass


if __name__ == '__main__':
    main()