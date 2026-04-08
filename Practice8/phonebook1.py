from connect import get_connection

def call_search(pattern):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_pattern(%s)", (pattern,))
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def call_insert_or_update(name, surname, phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL insert_or_update_user(%s, %s, %s)", (name, surname, phone))
    conn.commit()

    cur.close()
    conn.close()


def call_insert_many(names, surnames, phones):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "CALL insert_many_users(%s, %s, %s)",
        (names, surnames, phones)
    )
    conn.commit()

    cur.close()
    conn.close()


def call_pagination(limit, offset):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM get_paginated(%s, %s)", (limit, offset))
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def call_delete(value):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL delete_user(%s)", (value,))
    conn.commit()

    cur.close()
    conn.close()


# ===== MENU =====
if __name__ == "__main__":
    while True:
        print("\n1.Search\n2.Insert/Update\n3.Insert Many\n4.Pagination\n5.Delete\n0.Exit")
        choice = input("Choose: ")

        if choice == "1":
            call_search(input("Pattern: "))

        elif choice == "2":
            name = input("Name: ")
            surname = input("Surname: ")
            phone = input("Phone: ")
            call_insert_or_update(name, surname, phone)

        elif choice == "3":
            names = input("Names (comma): ").split(',')
            surnames = input("Surnames (comma): ").split(',')
            phones = input("Phones (comma): ").split(',')
            call_insert_many(names, surnames, phones)

        elif choice == "4":
            limit = int(input("Limit: "))
            offset = int(input("Offset: "))
            call_pagination(limit, offset)

        elif choice == "5":
            call_delete(input("Name or phone: "))

        elif choice == "0":
            break