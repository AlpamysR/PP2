import json
import csv
import os
import re

from connect import get_connection

# All files (CSV, JSON, SQL) are resolved relative to this script's folder,
# so the app works regardless of which directory the terminal is in.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _path(filename):
    """Return absolute path to a file inside the project folder."""
    return os.path.join(BASE_DIR, filename)

# --- Config ------------------------------------------------------------------

PAGE_SIZE = 5          # rows per page for paginated navigation


# --- Helpers -----------------------------------------------------------------

def _divider(width=90):
    print("-" * width)


def print_contacts(rows):
    """Pretty-print a list of contact rows."""
    if not rows:
        print("  (no contacts found)\n")
        return
    header = f"{'#':<4} {'Name':<20} {'Email':<25} {'Birthday':<12} {'Group':<10} Phones"
    _divider()
    print(header)
    _divider()
    for i, row in enumerate(rows, 1):
        cid, name, email, birthday, group_name, phones = row
        print(
            f"{i:<4} {str(name):<20} {str(email or ''):<25} "
            f"{str(birthday or ''):<12} {str(group_name or ''):<10} "
            f"{phones or ''}"
        )
    _divider()
    print()


# --- Schema & Procedures -----------------------------------------------------

def init_schema():
    """Execute schema.sql to create/extend tables."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        with open(_path("schema.sql"), "r", encoding="utf-8") as f:
            sql = f.read()
        # Execute statement by statement for clearer error messages
        statements = [s.strip() for s in re.split(r';\s*\n', sql) if s.strip()]
        for stmt in statements:
            try:
                cur.execute(stmt)
                conn.commit()
            except Exception as e:
                conn.rollback()
                msg = e.pgerror.splitlines()[0] if hasattr(e, 'pgerror') and e.pgerror else str(e)
                print(f"  Skipped (already applied?): {msg}")
        print("Schema initialised successfully.")
    except Exception as e:
        conn.rollback()
        print(f"  Error reading schema.sql: {e}")
    finally:
        cur.close()
        conn.close()


def load_procedures():
    """Execute procedures.sql to register PL/pgSQL objects."""
    conn = get_connection()
    cur = conn.cursor()
    with open(_path("procedures.sql"), "r", encoding="utf-8") as f:
        cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()
    print("Stored procedures / functions loaded.")


# --- 3.1  Contact CRUD -------------------------------------------------------

def _resolve_group(cur, group_name: str):
    """Return group_id for the given name, or None."""
    if not group_name:
        return None
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    row = cur.fetchone()
    return row[0] if row else None


def add_contact():
    """Interactively create a new contact with optional phones."""
    name = input("Name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    email    = input("Email (optional): ").strip() or None
    birthday = input("Birthday YYYY-MM-DD (optional): ").strip() or None

    print("Groups: Family | Work | Friend | Other")
    group_name = input("Group (optional): ").strip() or None

    conn = get_connection()
    cur  = conn.cursor()

    group_id = _resolve_group(cur, group_name)
    if group_name and group_id is None:
        print(f"  Warning: Group '{group_name}' not found - contact saved without group.")

    cur.execute(
        "INSERT INTO contacts (name, email, birthday, group_id) "
        "VALUES (%s, %s, %s, %s) RETURNING id",
        (name, email, birthday, group_id),
    )
    contact_id = cur.fetchone()[0]

    # Collect phone numbers
    print("Add phone numbers (leave blank to finish):")
    while True:
        phone = input("  Phone number: ").strip()
        if not phone:
            break
        ptype = input("  Type (home/work/mobile): ").strip().lower()
        if ptype not in ("home", "work", "mobile"):
            ptype = "mobile"
        cur.execute(
            "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
            (contact_id, phone, ptype),
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Contact '{name}' added (id={contact_id}).")


def delete_contact():
    """Delete a contact by name."""
    name = input("Contact name to delete: ").strip()
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE name = %s RETURNING id", (name,))
    deleted = cur.fetchone()
    if deleted:
        conn.commit()
        print(f"Contact '{name}' deleted.")
    else:
        conn.rollback()
        print(f"  Contact '{name}' not found.")
    cur.close()
    conn.close()


# --- 3.2  Search, Filter, Sort, Paginate -------------------------------------

def _fetch_contacts(search=None, group=None, sort_by="name", page=1):
    """
    Return (rows, total_count).
    search  - partial match on name / email / phone
    group   - exact group name filter
    sort_by - 'name' | 'birthday' | 'date'
    page    - 1-based page number
    """
    sort_map = {
        "name":     "c.name",
        "birthday": "c.birthday",
        "date":     "c.created_at",
    }
    order_col = sort_map.get(sort_by, "c.name")

    base = """
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE 1=1
    """
    params = []

    if search:
        base  += " AND (c.name ILIKE %s OR c.email ILIKE %s OR p.phone ILIKE %s)"
        like   = f"%{search}%"
        params += [like, like, like]

    if group:
        base  += " AND g.name = %s"
        params.append(group)

    select_cols = (
        "c.id, c.name, c.email, c.birthday, g.name AS group_name, "
        "STRING_AGG(p.phone || ' (' || COALESCE(p.type, '?') || ')', ', ') AS phones"
    )
    group_clause = "GROUP BY c.id, c.name, c.email, c.birthday, g.name"
    order_clause = f"ORDER BY {order_col}"
    limit_clause = f"LIMIT {PAGE_SIZE} OFFSET {(page - 1) * PAGE_SIZE}"

    full_query  = f"SELECT {select_cols} {base} {group_clause} {order_clause} {limit_clause}"
    count_query = f"SELECT COUNT(DISTINCT c.id) {base}"

    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(count_query, params)
    total = cur.fetchone()[0]
    cur.execute(full_query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows, total


def _paginated_view(search=None, group=None, sort_by="name"):
    """Paginated console loop: next / prev / quit."""
    page = 1
    while True:
        rows, total = _fetch_contacts(search=search, group=group,
                                      sort_by=sort_by, page=page)
        total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        print(f"\n  Page {page} / {total_pages}  |  {total} contact(s) total")
        print_contacts(rows)

        if total_pages == 1:
            break

        cmd = input("  next | prev | quit : ").strip().lower()
        if cmd == "next":
            if page < total_pages:
                page += 1
            else:
                print("  Already on the last page.")
        elif cmd == "prev":
            if page > 1:
                page -= 1
            else:
                print("  Already on the first page.")
        elif cmd == "quit":
            break


def list_all():
    sort_by = input("Sort by (name / birthday / date) [name]: ").strip() or "name"
    _paginated_view(sort_by=sort_by)


def search_contacts():
    """Search by name, email, or phone (partial match)."""
    query   = input("Search query: ").strip()
    sort_by = input("Sort by (name / birthday / date) [name]: ").strip() or "name"
    _paginated_view(search=query, sort_by=sort_by)


def filter_by_group():
    """Show contacts belonging to a chosen group."""
    print("Groups: Family | Work | Friend | Other")
    group   = input("Group name: ").strip()
    sort_by = input("Sort by (name / birthday / date) [name]: ").strip() or "name"
    _paginated_view(group=group, sort_by=sort_by)


# --- 3.4  Stored Procedures via Python ---------------------------------------

def add_phone_to_contact():
    """Call add_phone(p_contact_name, p_phone, p_type) stored procedure."""
    name  = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    ptype = input("Type (home / work / mobile): ").strip().lower()

    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
        print("Phone added.")
    except Exception as exc:
        conn.rollback()
        print(f"  Error: {exc}")
    finally:
        cur.close()
        conn.close()


def move_contact_to_group():
    """Call move_to_group(p_contact_name, p_group_name) stored procedure."""
    name  = input("Contact name: ").strip()
    group = input("Target group name: ").strip()

    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
        print(f"Moved '{name}' to group '{group}'.")
    except Exception as exc:
        conn.rollback()
        print(f"  Error: {exc}")
    finally:
        cur.close()
        conn.close()


# --- 3.3  Export / Import JSON -----------------------------------------------

def export_to_json():
    """Write all contacts (phones + group) to a .json file."""
    filename = input("Output file [contacts.json]: ").strip() or "contacts.json"

    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday::TEXT, g.name
        FROM   contacts c
        LEFT   JOIN groups g ON c.group_id = g.id
        ORDER  BY c.name
    """)
    raw = cur.fetchall()

    contacts = []
    for cid, name, email, birthday, group_name in raw:
        cur2 = conn.cursor()
        cur2.execute(
            "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id",
            (cid,),
        )
        phones = [{"phone": p, "type": t} for p, t in cur2.fetchall()]
        cur2.close()
        contacts.append({
            "name":     name,
            "email":    email,
            "birthday": birthday,
            "group":    group_name,
            "phones":   phones,
        })

    cur.close()
    conn.close()

    with open(_path(filename), "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(contacts)} contact(s) to '{filename}'.")


def import_from_json():
    """Read contacts from a .json file; ask skip / overwrite on duplicate name."""
    filename = input("Input file [contacts.json]: ").strip() or "contacts.json"
    if not os.path.exists(_path(filename)):
        print(f"  File '{filename}' not found.")
        return

    with open(_path(filename), "r", encoding="utf-8") as f:
        contacts = json.load(f)

    conn = get_connection()
    cur  = conn.cursor()
    added = skipped = overwritten = 0

    for c in contacts:
        name       = c.get("name", "").strip()
        email      = c.get("email")
        birthday   = c.get("birthday")
        group_name = c.get("group")
        phones     = c.get("phones", [])

        if not name:
            continue

        # Duplicate check
        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()

        if existing:
            action = input(
                f"  '{name}' already exists - (s)kip / (o)verwrite? "
            ).strip().lower()
            if action == "o":
                cur.execute("DELETE FROM contacts WHERE id = %s", (existing[0],))
                overwritten += 1
            else:
                skipped += 1
                continue
        else:
            added += 1

        # Resolve / create group
        group_id = None
        if group_name:
            cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
            row = cur.fetchone()
            if row:
                group_id = row[0]
            else:
                cur.execute(
                    "INSERT INTO groups (name) VALUES (%s) RETURNING id",
                    (group_name,),
                )
                group_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO contacts (name, email, birthday, group_id) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            (name, email, birthday, group_id),
        )
        contact_id = cur.fetchone()[0]

        for p in phones:
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                (contact_id, p.get("phone"), p.get("type")),
            )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Import done - added: {added}, overwritten: {overwritten}, skipped: {skipped}.")


# --- 3.3  Extended CSV Import ------------------------------------------------

def import_from_csv():
    """
    Import contacts from CSV.
    Expected columns: name, email, birthday, group, phone, phone_type
    """
    eee = "sample.csv"
    if not os.path.exists(_path(eee)):
        print(f"  File '{eee}' not found.")
        return

    conn = get_connection()
    cur  = conn.cursor()
    added = phones_added = 0

    with open(_path(eee), "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name       = row.get("name", "").strip()
            email      = row.get("email", "").strip() or None
            birthday   = row.get("birthday", "").strip() or None
            group_name = row.get("group", "").strip() or None
            phone      = row.get("phone", "").strip() or None
            phone_type = row.get("phone_type", "mobile").strip() or "mobile"

            if not name:
                continue

            # Resolve group
            group_id = None
            if group_name:
                cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                g = cur.fetchone()
                if g:
                    group_id = g[0]
                else:
                    cur.execute(
                        "INSERT INTO groups (name) VALUES (%s) RETURNING id",
                        (group_name,),
                    )
                    group_id = cur.fetchone()[0]

            # Upsert contact
            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()
            if existing:
                contact_id = existing[0]
                # Update email/birthday/group if provided
                cur.execute(
                    "UPDATE contacts SET email = COALESCE(%s, email), "
                    "birthday = COALESCE(%s::DATE, birthday), "
                    "group_id = COALESCE(%s, group_id) WHERE id = %s",
                    (email, birthday, group_id, contact_id),
                )
            else:
                cur.execute(
                    "INSERT INTO contacts (name, email, birthday, group_id) "
                    "VALUES (%s, %s, %s, %s) RETURNING id",
                    (name, email, birthday, group_id),
                )
                contact_id = cur.fetchone()[0]
                added += 1

            # Add phone if present
            if phone:
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                    (contact_id, phone, phone_type),
                )
                phones_added += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"CSV import done - {added} new contact(s), {phones_added} phone(s) added.")


# --- Main Menu ---------------------------------------------------------------

MENU = """
========================================
        PHONEBOOK - Main Menu
========================================
  1.  List all contacts
  2.  Search contacts
  3.  Filter by group
  4.  Add contact
  5.  Delete contact
  6.  Add phone to contact
  7.  Move contact to group
----------------------------------------
  8.  Export to JSON
  9.  Import from JSON
  10. Import from CSV
----------------------------------------
  11. Initialise schema
  12. Load stored procedures
  0.  Exit
========================================
"""

ACTIONS = {
    "1":  list_all,
    "2":  search_contacts,
    "3":  filter_by_group,
    "4":  add_contact,
    "5":  delete_contact,
    "6":  add_phone_to_contact,
    "7":  move_contact_to_group,
    "8":  export_to_json,
    "9":  import_from_json,
    "10": import_from_csv,
    "11": init_schema,
    "12": load_procedures,
}


def main():
    print("\n  Welcome to the Extended Phonebook!")
    while True:
        print(MENU)
        choice = input("  Choice: ").strip()
        if choice == "0":
            print("  Goodbye!")
            break
        action = ACTIONS.get(choice)
        if action:
            print()
            action()
        else:
            print("  Invalid choice. Try again.")


if __name__ == "__main__":
    main()