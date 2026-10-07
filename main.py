"""Menu-driven Library Management System.  Run:  python main.py"""

from datetime import date, timedelta

from exceptions import LibraryError
from library import FINE_PER_DAY, LOAN_DAYS, Library
from models import Admin, Member

ADMIN_PASSWORD = "admin123"   # demo only - never hard-code passwords in real projects


def read_int(prompt, minimum=1):
    value = input(prompt).strip()
    if not value.isdigit() or int(value) < minimum:
        raise LibraryError(f"Please enter a number >= {minimum}.")
    return int(value)


def print_list(items, empty_message):
    if not items:
        print(empty_message)
    for item in items:
        print("  ", item)


def admin_session(library, admin):
    actions = {
        "1": lambda: print("Added:", library.add_book(
            input("Title: "), input("Author: "), read_int("Copies: "))),
        "2": lambda: (library.remove_book(input("Book id to remove: ")), print("Book removed.")),
        "3": lambda: print("Registered member with id", library.register_member(input("Name: ")).user_id),
        "4": lambda: print_list(library.all_books(), "No books yet."),
        "5": lambda: print_list([f"{m.user_id} - {m.name} ({len(m.borrowed)} borrowed)"
                                 for m in library.all_members()], "No members yet."),
    }
    run_menu(admin, actions)


def member_session(library, member):
    def borrow():
        issued = library.issue_book(member.user_id, input("Book id to borrow: "))
        print(f"Issued. Return by {issued + timedelta(days=LOAN_DAYS)} to avoid a fine "
              f"of Rs.{FINE_PER_DAY}/day.")

    def give_back():
        fine = library.return_book(member.user_id, input("Book id to return: "))
        print("Returned." + (f" Late fine: Rs.{fine}" if fine else " No fine."))

    def my_books():
        rows = [f"{library.get_book(bid).title} (issued {d})" for bid, d in member.borrowed.items()]
        print_list(rows, "You have no borrowed books.")

    actions = {
        "1": lambda: print_list(library.search_books(input("Title or author: ")), "No match found."),
        "2": borrow,
        "3": give_back,
        "4": my_books,
    }
    run_menu(member, actions)


def run_menu(user, actions):
    """Generic menu loop - works for any User subclass (polymorphism)."""
    while True:
        print(f"\n--- {user.role} menu: {user.name} ---")
        for key, label in user.get_menu().items():
            print(f"{key}. {label}")
        choice = input("Choose: ").strip()
        if choice == "0":
            return
        action = actions.get(choice)
        if action is None:
            print("Invalid choice.")
            continue
        try:
            action()
        except LibraryError as error:      # custom exceptions -> friendly message
            print("Error:", error)


def main():
    library = Library()
    while True:
        print("\n===== LIBRARY MANAGEMENT SYSTEM =====")
        print("1. Admin login\n2. Member login\n0. Exit")
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                if input("Password: ") == ADMIN_PASSWORD:
                    admin_session(library, Admin("A001", "Admin"))
                else:
                    print("Wrong password.")
            elif choice == "2":
                member = library.get_member(input("Member id (e.g. M001): "))
                member_session(library, member)
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")
        except LibraryError as error:
            print("Error:", error)


if __name__ == "__main__":
    main()
