"""Domain classes: Book, User (base), Admin and Member (child classes)."""

from datetime import date

from exceptions import InvalidInputError


class Book:
    """A book in the library. Attributes are private and exposed via properties."""

    def __init__(self, book_id, title, author, copies=1):
        if not title.strip() or not author.strip():
            raise InvalidInputError("Title and author cannot be empty.")
        if copies < 1:
            raise InvalidInputError("Copies must be at least 1.")
        self._book_id = book_id
        self._title = title.strip()
        self._author = author.strip()
        self._total_copies = copies
        self._available_copies = copies

    # --- read-only access (encapsulation) ---
    @property
    def book_id(self):
        return self._book_id

    @property
    def title(self):
        return self._title

    @property
    def author(self):
        return self._author

    @property
    def total_copies(self):
        return self._total_copies

    @property
    def available_copies(self):
        return self._available_copies

    # --- behaviour ---
    def is_available(self):
        return self._available_copies > 0

    def issue_copy(self):
        self._available_copies -= 1

    def return_copy(self):
        self._available_copies += 1

    def matches(self, keyword):
        """Case-insensitive search on title or author."""
        keyword = keyword.lower()
        return keyword in self._title.lower() or keyword in self._author.lower()

    def to_dict(self):
        return {
            "book_id": self._book_id,
            "title": self._title,
            "author": self._author,
            "total_copies": self._total_copies,
            "available_copies": self._available_copies,
        }

    @classmethod
    def from_dict(cls, data):
        book = cls(data["book_id"], data["title"], data["author"], data["total_copies"])
        book._available_copies = data["available_copies"]
        return book

    def __str__(self):
        return (f"[{self._book_id}] {self._title} by {self._author} "
                f"({self._available_copies}/{self._total_copies} available)")


class User:
    """Base class for every person who uses the system."""

    def __init__(self, user_id, name):
        if not name.strip():
            raise InvalidInputError("Name cannot be empty.")
        self._user_id = user_id
        self._name = name.strip()

    @property
    def user_id(self):
        return self._user_id

    @property
    def name(self):
        return self._name

    @property
    def role(self):
        return "User"

    def get_menu(self):
        """Child classes override this (polymorphism)."""
        return {"0": "Exit"}


class Admin(User):
    """Admin can manage books and members."""

    @property
    def role(self):
        return "Admin"

    def get_menu(self):
        return {
            "1": "Add a book",
            "2": "Remove a book",
            "3": "Register a member",
            "4": "View all books",
            "5": "View all members",
            "0": "Logout",
        }


class Member(User):
    """Member can search, borrow and return books."""

    MAX_BOOKS = 3

    def __init__(self, user_id, name, borrowed=None):
        super().__init__(user_id, name)
        # {book_id: issue_date (datetime.date)}
        self._borrowed = borrowed if borrowed is not None else {}

    @property
    def role(self):
        return "Member"

    @property
    def borrowed(self):
        return dict(self._borrowed)  # return a copy to protect internal state

    def can_borrow(self):
        return len(self._borrowed) < self.MAX_BOOKS

    def has_book(self, book_id):
        return book_id in self._borrowed

    def add_borrowed(self, book_id, issue_date):
        self._borrowed[book_id] = issue_date

    def remove_borrowed(self, book_id):
        return self._borrowed.pop(book_id)

    def get_menu(self):
        return {
            "1": "Search books",
            "2": "Borrow a book",
            "3": "Return a book",
            "4": "My borrowed books",
            "0": "Logout",
        }

    def to_dict(self):
        return {
            "member_id": self._user_id,
            "name": self._name,
            "borrowed": {bid: d.isoformat() for bid, d in self._borrowed.items()},
        }

    @classmethod
    def from_dict(cls, data):
        borrowed = {bid: date.fromisoformat(d) for bid, d in data["borrowed"].items()}
        return cls(data["member_id"], data["name"], borrowed)
