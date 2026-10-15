# Susu Group Tracker

A small command-line program that manages one rotating savings group (susu) in GHS.
Python 3.10+, standard library only (no installs needed).

## Run

    python -m susu

Commands:

| Command | What it does |
|---|---|
| `new 50.00` | Create the group with a weekly contribution |
| `add Ama` | Add a member (join order = payout order) |
| `pay Ama 30.00` | Record a (partial) payment for the current week |
| `close` | Close the week: pays out if everyone paid in full, otherwise lists who owes what |
| `report` | Current week, paid in full, owing, payout history |
| `quit` | Exit |

Use quotes for names with spaces: `add "Ama Mensah"`.

## Test

    python -m unittest discover -s tests -v

## Layout

    susu/money.py   exact money parsing/validation (Decimal)
    susu/group.py   all business rules, no I/O
    susu/errors.py  SusuError
    susu/cli.py     interactive shell
    tests/          unit tests
