"""Custom exceptions used across the Library Management System."""


class LibraryError(Exception):
    """Base class for all library-related errors."""


class BookNotFoundError(LibraryError):
    """Raised when a book id does not exist."""


class MemberNotFoundError(LibraryError):
    """Raised when a member id does not exist."""


class BookNotAvailableError(LibraryError):
    """Raised when all copies of a book are already issued."""


class BorrowLimitError(LibraryError):
    """Raised when a member tries to borrow more than the allowed books."""


class InvalidInputError(LibraryError):
    """Raised when user input is empty or in a wrong format."""
