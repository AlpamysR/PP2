import csv
from connect import get_connection
import os
1
# 1. Insert from CSV
def insert_from_csv():
    conn = get_connection()
    cur = conn.cursor()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "contacts.csv")
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cur.execute(
                    "INSERT INTO contacts (first_name, phone) VALUES (%s, %s) ON CONFLICT (phone) DO NOTHING",
                    (row['first_name'], row['phone'])
                )
            except Exception as e:
                print("Error:", e)

    conn.commit()
    cur.close()
    conn.close()
    print("CSV data inserted.")
    
# 2. Insert from console

def insert_from_console():
    name = input("Enter name: ")
    phone = input("Enter phone: ")

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO contacts (first_name, phone) VALUES (%s, %s)",
            (name, phone)
        )
        conn.commit()
        print("Contact added.")
    except Exception as e:
        print("Error:", e)

    cur.close()
    conn.close()


# 3. Update contact
def update_contact():
    phone = input("Enter phone of contact to update: ")
    new_name = input("New name (leave empty to skip): ")
    new_phone = input("New phone (leave empty to skip): ")

    conn = get_connection()
    cur = conn.cursor()

    if new_name:
        cur.execute(
            "UPDATE contacts SET first_name=%s WHERE phone=%s",
            (new_name, phone)
        )

    if new_phone:
        cur.execute(
            "UPDATE contacts SET phone=%s WHERE phone=%s",
            (new_phone, phone)
        )

    conn.commit()
    print("Contact updated.")

    cur.close()
    conn.close()


# 4. Query contacts
def query_contacts():
    print("1. Show all")
    print("2. Search by name")
    print("3. Search by phone prefix")

    choice = input("Choose: ")

    conn = get_connection()
    cur = conn.cursor()

    if choice == "1":
        cur.execute("SELECT * FROM contacts")

    elif choice == "2":
        name = input("Enter name: ")
        cur.execute(
            "SELECT * FROM contacts WHERE first_name ILIKE %s",
            ('%' + name + '%',)
        )

    elif choice == "3":
        prefix = input("Enter prefix: ")
        cur.execute(
            "SELECT * FROM contacts WHERE phone LIKE %s",
            (prefix + '%',)
        )

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


# 5. Delete contact
def delete_contact():
    print("1. Delete by name")
    print("2. Delete by phone")

    choice = input("Choose: ")

    conn = get_connection()
    cur = conn.cursor()

    if choice == "1":
        name = input("Enter name: ")
        cur.execute(
            "DELETE FROM contacts WHERE first_name=%s",
            (name,)
        )

    elif choice == "2":
        phone = input("Enter phone: ")
        cur.execute(
            "DELETE FROM contacts WHERE phone=%s",
            (phone,)
        )

    conn.commit()
    print("Contact deleted.")

    cur.close()
    conn.close()


# MENU
def menu():
    while True:
        print("\n--- PHONEBOOK ---")
        print("1. Insert from CSV")
        print("2. Add contact")
        print("3. Update contact")
        print("4. Query contacts")
        print("5. Delete contact")
        print("0. Exit")

        choice = input("Select: ")

        if choice == "1":
            insert_from_csv()
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            update_contact()
        elif choice == "4":
            query_contacts()
        elif choice == "5":
            delete_contact()
        elif choice == "0":
            break
        else:
            print("Invalid option.")
            
if __name__ == "__main__":
    menu()

