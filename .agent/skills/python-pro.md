# Python Pro Skill

## Overview
Advanced Python programming techniques, focusing on clean code, performance, and modern features relevant to Django development.

## Modern Python Features (3.10+)
- **Type Hinting**: Use strict type hints (`typing.List`, `typing.Optional`, or modern `list[]`, `str | None`).
- **Data Classes**: Use `@dataclass` for data-holding objects to reduce boilerplate.
- **Pattern Matching**: Leverage `match/case` for complex control flow.
- **Walrus Operator**: Use `:=` for assignment within expressions where it improves readability.

## Code Style & Quality
- **PEP 8**: Adhere strictly. Use linters (Ruff/Black).
- **Docstrings**: Google or NumPy style docstrings for all complex functions.
- **Composition over Inheritance**: Prefer composition/mixins over deep inheritance trees.
- **Context Managers**: Use `with` statement and custom context managers (`@contextlib.contextmanager`) for resource management.

## Performance
- **Generators**: Use generators (`yield`) for processing large datasets to save memory.
- **List Comprehensions**: Use for concise transformation, but switch to loops if it gets too complex.
- **itertools/functools**: Master the standard library tools for efficient iteration and functional patterns.

## Django Pro Tips
- **QuerySet Optimization**:
  - `select_related()` for OneToOne/ForeignKey (SQL Join).
  - `prefetch_related()` for ManyToMany/Reverse FK (Separate Query).
  - `only()` / `defer()` to fetch necessary fields only.
  - `exists()` instead of `count() > 0`.
  - `iterator()` for large data export/processing.
- **Fat Models / Thin Views**: Encapsulate business logic in Model methods or Service layers/Managers, not within Views/API endpoints.
- **Signals**: Use sparingly. They obfuscate logic flow. Prefer overriding `save()` or using Service methods.
- **F Expressions**: Use `F()` for atomic database updates (race condition prevention).

## Testing
- **Pytest**: Prefer `pytest` over `unittest`.
- **Fixtures**: Use `conftest.py` and fixtures for reusable test state.
- **Factories**: Use `factory_boy` instead of manual object creation.
