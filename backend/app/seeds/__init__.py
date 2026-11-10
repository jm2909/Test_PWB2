"""Seed registry. Domain modules call register() at import; run_all() runs them in order.

A seed function takes a Session and must be idempotent (safe to run any number of times).
Lower `order` runs first; ties run in registration order. Modules in this package are
discovered automatically by run_all(), so adding a domain seed is just adding a module.
"""

import importlib
import pkgutil
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.orm import Session

SeedFn = Callable[[Session], None]


@dataclass(frozen=True)
class SeedEntry:
    name: str
    order: int
    fn: SeedFn


_REGISTRY: dict[str, SeedEntry] = {}


def register(name: str, order: int = 100) -> Callable[[SeedFn], SeedFn]:
    def decorator(fn: SeedFn) -> SeedFn:
        _REGISTRY[name] = SeedEntry(name=name, order=order, fn=fn)
        return fn

    return decorator


def registered() -> list[SeedEntry]:
    return sorted(_REGISTRY.values(), key=lambda e: e.order)


def discover() -> None:
    for module in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{module.name}")


def run_all(db: Session) -> list[str]:
    discover()
    ran: list[str] = []
    for entry in registered():
        entry.fn(db)
        db.commit()
        ran.append(entry.name)
    return ran
