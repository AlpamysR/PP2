from connect import get_connection


def search():
    keyword = input("Search: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s)", (keyword,))
    rows = cur.fetchall()

    for row in rows:
        print(row)

    conn.close()


def add_or_update():
    name = input("Name: ")
    phone = input("Phone: ")
    email = input("Email: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "CALL upsert_contact(%s, %s, %s)",
        (name, phone, email)
    )

    conn.commit()
    conn.close()


def delete():
    value = input("Enter name or phone: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL delete_contact(%s)", (value,))
    conn.commit()

    conn.close()


def pagination():
    limit = int(input("Limit: "))
    offset = int(input("Offset: "))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM get_contacts_paginated(%s, %s)",
        (limit, offset)
    )

    rows = cur.fetchall()
    for row in rows:
        print(row)

    conn.close()


def menu():
    while True:
        print("\n1. Search")
        print("2. Add/Update")
        print("3. Delete")
        print("4. Pagination")
        print("5. Exit")

        choice = input("Choose: ")

        if choice == "1":
            search()
        elif choice == "2":
            add_or_update()
        elif choice == "3":
            delete()
        elif choice == "4":
            pagination()
        elif choice == "5":
            break


if __name__ == "__main__":
    menu()
