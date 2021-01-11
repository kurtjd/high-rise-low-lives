from __future__ import annotations
import game_entities.actor


def use_stitch(src_actor: game_entities.actor.Actor) -> None:
    """Called after the drug 'Stitch' is used."""

    src_actor.health += 20
