import entities


def use_stitch(src_actor: "entities.Actor") -> None:
    """Called after the drug 'Stitch' is used."""

    src_actor.health += 20
