"""Library class: all business rules (issue, return, search, fines)."""

from datetime import date

import storage
from exceptions import (BookNotAvailableError, BookNotFoundError, BorrowLimitError,
                        InvalidInputError, MemberNotFoundError)
from models import Book, Member

LOAN_DAYS = 14          # books must be returned within 14 days
FINE_PER_DAY = 2        # Rs. 2 per day after the due date


class Library:
    def __init__(self):
        self._books = {b["book_id"]: Book.from_dict(b) for b in storage.load_json(storage.BOOKS_FILE)}
        self._members = {m["member_id"]: Member.from_dict(m) for m in storage.load_json(storage.MEMBERS_FILE)}

    # ---------- persistence ----------
    def save(self):
        storage.save_json(storage.BOOKS_FILE, [b.to_dict() for b in self._books.values()])
        storage.save_json(storage.MEMBERS_FILE, [m.to_dict() for m in self._members.values()])

    # ---------- helpers ----------
    def _next_id(self, prefix, existing):
        numbers = [int(key[1:]) for key in existing if key[1:].isdigit()]
        return f"{prefix}{max(numbers, default=0) + 1:03d}"

    def get_book(self, book_id):
        try:
            return self._books[book_id.upper()]
        except KeyError:
            raise BookNotFoundError(f"No book found with id '{book_id}'.")

    def get_member(self, member_id):
        try:
            return self._members[member_id.upper()]
        except KeyError:
            raise MemberNotFoundError(f"No member found with id '{member_id}'.")

    # ---------- admin operations ----------
    def add_book(self, title, author, copies):
        book = Book(self._next_id("B", self._books), title, author, copies)
        self._books[book.book_id] = book
        self.save()
        return book

    def remove_book(self, book_id):
        book = self.get_book(book_id)
        if book.available_copies != book.total_copies:
            raise InvalidInputError("Cannot remove a book that is currently issued.")
        del self._books[book.book_id]
        self.save()

    def register_member(self, name):
        member = Member(self._next_id("M", self._members), name)
        self._members[member.user_id] = member
        self.save()
        return member

    def all_books(self):
        return list(self._books.values())

    def all_members(self):
        return list(self._members.values())

    # ---------- member operations ----------
    def search_books(self, keyword):
        if not keyword.strip():
            raise InvalidInputError("Search keyword cannot be empty.")
        return [b for b in self._books.values() if b.matches(keyword)]

    def issue_book(self, member_id, book_id, issue_date=None):
        member = self.get_member(member_id)
        book = self.get_book(book_id)
        if not member.can_borrow():
            raise BorrowLimitError(f"{member.name} already has {Member.MAX_BOOKS} books issued.")
        if member.has_book(book.book_id):
            raise InvalidInputError("You already have a copy of this book.")
        if not book.is_available():
            raise BookNotAvailableError(f"'{book.title}' is currently not available.")
        book.issue_copy()
        issue_date = issue_date or date.today()
        member.add_borrowed(book.book_id, issue_date)
        self.save()
        return issue_date

    def return_book(self, member_id, book_id, return_date=None):
        """Return a book and get the late fine (0 if returned on time)."""
        member = self.get_member(member_id)
        book = self.get_book(book_id)
        if not member.has_book(book.book_id):
            raise InvalidInputError("This member has not borrowed that book.")
        issue_date = member.remove_borrowed(book.book_id)
        book.return_copy()
        fine = self.calculate_fine(issue_date, return_date or date.today())
        self.save()
        return fine

    @staticmethod
    def calculate_fine(issue_date, return_date):
        days_late = (return_date - issue_date).days - LOAN_DAYS
        return max(days_late, 0) * FINE_PER_DAY
