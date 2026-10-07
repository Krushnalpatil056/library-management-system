# Library Management System

Menu-driven Python application built with OOP. No external libraries needed.

## Run
```bash
python main.py
```
- **Admin** password: `admin123` (demo only) – add/remove books, register members.
- **Members** `M001` (Amit Sharma) and `M002` (Neha Kulkarni) are pre-loaded – search, borrow, return books.

## Features
- Classes: `Book`, `User` (base), `Admin` and `Member` (inherit from `User`), `Library`
- Encapsulation with private attributes and properties; polymorphic `get_menu()`
- Custom exceptions (`BookNotFoundError`, `BookNotAvailableError`, `BorrowLimitError`, ...)
- JSON persistence in `data/`
- Rules: 14-day loan, Rs.2/day late fine, maximum 3 books per member

## Files
| File | Purpose |
|------|---------|
| `main.py` | Menus and user interaction |
| `library.py` | Business logic (issue, return, search, fines) |
| `models.py` | Book, User, Admin, Member classes |
| `storage.py` | Read/write JSON files |
| `exceptions.py` | Custom exceptions |
| `data/` | Sample books and members |
