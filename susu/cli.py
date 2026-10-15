"""Simple interactive command line. Run: python -m susu"""
import cmd
import shlex

from .group import Group, SusuError
from .money import fmt


class SusuShell(cmd.Cmd):
    intro = "Susu Group Tracker. Type 'help' for commands."
    prompt = "susu> "

    def __init__(self):
        super().__init__()
        self.group: Group | None = None

    def _need_group(self) -> bool:
        if self.group is None:
            print("Create a group first: new <weekly_amount>")
            return False
        return True

    def _run(self, fn, *args):
        try:
            fn(*args)
        except SusuError as e:
            print(f"Error: {e}")

    def do_new(self, arg):
        """new <weekly_amount_GHS>  - create a group, e.g. new 50.00"""
        def go():
            self.group = Group(arg.strip())
            print(f"Group created. Weekly contribution: GHS {fmt(self.group.weekly_amount)}")
        self._run(go)

    def do_add(self, arg):
        """add <name>  - add a member (only before any payment is made)"""
        if not self._need_group():
            return
        def go():
            self.group.add_member(arg)
            print(f"Added {arg.strip()} (position {len(self.group.members)}).")
        self._run(go)

    def do_pay(self, arg):
        """pay <name> <amount>  - record a contribution; use quotes for names with spaces"""
        if not self._need_group():
            return
        def go():
            parts = shlex.split(arg)
            if len(parts) != 2:
                raise SusuError('Usage: pay <name> <amount>')
            left = self.group.record_contribution(parts[0], parts[1])
            print(f"Recorded. {parts[0]} still owes GHS {fmt(left)} this week.")
        self._run(go)

    def do_close(self, arg):
        """close  - close the current week and pay out if everyone paid in full"""
        if not self._need_group():
            return
        def go():
            res = self.group.close_week()
            if res.closed:
                p = res.payout
                print(f"Week {p.week} closed. {p.recipient} receives GHS {fmt(p.amount)}.")
                if self.group.is_complete:
                    print("Cycle complete: everyone has been paid.")
                else:
                    print(f"Week {self.group.current_week} begins.")
            else:
                print("Cannot close week. No payout made.")
                for name, amt in res.owing.items():
                    print(f"  {name} owes {fmt(amt)}")
        self._run(go)

    def do_report(self, arg):
        """report  - show the current week, who paid, who owes and payout history"""
        if not self._need_group():
            return
        r = self.group.report()
        print(f"Week: {r.week}" + ("  (cycle complete)" if r.complete else ""))
        if r.next_recipient:
            print(f"Next recipient: {r.next_recipient}")
        print("Paid in full: " + (", ".join(r.paid_in_full) or "nobody"))
        if r.owing:
            print("Owing:")
            for n, a in r.owing.items():
                print(f"  {n} owes {fmt(a)}")
        else:
            print("Owing: nobody")
        print("Payout history:" + ("" if r.payouts else " none yet"))
        for p in r.payouts:
            print(f"  Week {p.week}: {p.recipient} received GHS {fmt(p.amount)}")

    def do_quit(self, arg):
        """quit  - exit"""
        return True

    do_exit = do_quit
    do_EOF = do_quit


def main():
    SusuShell().cmdloop()
