from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "backpack.json"


@dataclass(frozen=True, slots=True)
class StartingWeapon:
    key: str
    reserve_ammo: int


@dataclass(frozen=True, slots=True)
class StartingItem:
    key: str
    amount: int


@dataclass(frozen=True, slots=True)
class BackpackConfig:
    slots: int
    starting_weapon: StartingWeapon
    starting_items: tuple[StartingItem, ...]


def load_backpack_config() -> BackpackConfig:
    data = _read_config()
    weapon = dict(data.get("starting_weapon", {}))
    items = tuple(
        StartingItem(str(item.get("key", "")), max(1, int(item.get("amount", 1))))
        for item in data.get("starting_items", [])
        if item.get("key")
    )
    return BackpackConfig(
        slots=max(10, min(80, int(data.get("slots", 30)))),
        starting_weapon=StartingWeapon(str(weapon.get("key", "pistol")), max(0, int(weapon.get("reserve_ammo", 48)))),
        starting_items=items or (StartingItem("apple", 2), StartingItem("bandage", 1), StartingItem("cloth", 2)),
    )


def _read_config() -> dict[str, object]:
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
