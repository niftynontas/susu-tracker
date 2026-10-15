"""Core susu logic. No I/O here, so it is easy to test."""
from dataclasses import dataclass
from decimal import Decimal

from .errors import SusuError
from .money import CENT, parse_money


@dataclass(frozen=True)
class Payout:
    week: int
    recipient: str
    amount: Decimal


@dataclass(frozen=True)
class CloseResult:
    closed: bool
    payout: Payout | None
    owing: dict  # name -> Decimal still owed (empty when closed)


@dataclass(frozen=True)
class Report:
    week: int
    complete: bool
    next_recipient: str | None
    paid_in_full: list
    owing: dict
    payouts: list


class Group:
    def __init__(self, weekly_amount):
        self.weekly_amount = parse_money(weekly_amount)
        self._members: list[str] = []          # join order = payout order
        self._paid: dict[str, Decimal] = {}    # key -> paid this week
        self.current_week = 1
        self.payouts: list[Payout] = []

    # ---------- helpers ----------
    @staticmethod
    def _key(name: str) -> str:
        return name.strip().casefold()

    @property
    def members(self) -> list[str]:
        return list(self._members)

    @property
    def is_complete(self) -> bool:
        """Every member has received the pot once: the cycle is finished."""
        return bool(self._members) and len(self.payouts) == len(self._members)

    @property
    def has_started(self) -> bool:
        return self.current_week > 1 or any(p > 0 for p in self._paid.values())

    def _find(self, name: str) -> str:
        key = self._key(name or "")
        for m in self._members:
            if self._key(m) == key:
                return m
        raise SusuError(f"Unknown member '{name}'.")

    def _owed(self, member: str) -> Decimal:
        return self.weekly_amount - self._paid[self._key(member)]

    def _require_active(self):
        if self.is_complete:
            raise SusuError("The cycle is complete: every member has been paid.")

    # ---------- commands ----------
    def add_member(self, name: str) -> None:
        name = (name or "").strip()
        if not name:
            raise SusuError("Member name cannot be empty.")
        if any(self._key(m) == self._key(name) for m in self._members):
            raise SusuError(f"Member '{name}' already exists.")
        if self.has_started:
            raise SusuError(
                "Members can only be added before the first contribution is recorded."
            )
        self._members.append(name)
        self._paid[self._key(name)] = Decimal("0.00")

    def record_contribution(self, name: str, amount, week: int | None = None) -> Decimal:
        """Record a (possibly partial) payment. Returns what the member still owes."""
        self._require_active()
        if week is not None and week != self.current_week:
            raise SusuError(
                f"Can only record contributions for the current week ({self.current_week})."
            )
        member = self._find(name)
        amount = parse_money(amount)
        owed = self._owed(member)
        if amount > owed:
            raise SusuError(f"{member} only owes {owed:.2f} this week; got {amount:.2f}.")
        self._paid[self._key(member)] += amount
        return self._owed(member)

    def amounts_owing(self) -> dict:
        return {m: self._owed(m) for m in self._members if self._owed(m) > 0}

    def close_week(self) -> CloseResult:
        self._require_active()
        if not self._members:
            raise SusuError("Add at least one member before closing a week.")
        owing = self.amounts_owing()
        if owing:
            return CloseResult(False, None, owing)
        recipient = self._members[self.current_week - 1]
        pot = (self.weekly_amount * len(self._members)).quantize(CENT)
        payout = Payout(self.current_week, recipient, pot)
        self.payouts.append(payout)
        self.current_week += 1
        for key in self._paid:
            self._paid[key] = Decimal("0.00")
        return CloseResult(True, payout, {})

    def report(self) -> Report:
        paid = [m for m in self._members if self._owed(m) == 0]
        nxt = None if self.is_complete or not self._members else self._members[self.current_week - 1]
        return Report(self.current_week, self.is_complete, nxt, paid,
                      self.amounts_owing(), list(self.payouts))
