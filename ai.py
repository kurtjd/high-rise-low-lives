import entities


# Each Actor carries a reference to one of these AI functions depending on its abilities and style.

# For intelligent actors that like to fight up-close and personal.
def smart_melee(src_actor: entities.Actor, game_actors: list[entities.Actor]) -> None:
    # If not currently targeting an actor, find the first one.
    if src_actor.atk_target is None:
        for entity in game_actors:
            if entity is not src_actor:
                src_actor.atk_target = entity
                break

    # Simply attempt to move toward target, and stepping onto target attacks it.
    if src_actor.x - src_actor.atk_target.x > 0:
        src_actor.attempt_move(-1, 0)
    elif src_actor.x - src_actor.atk_target.x < 0:
        src_actor.attempt_move(1, 0)
    if src_actor.y - src_actor.atk_target.y > 0:
        src_actor.attempt_move(0, -1)
    elif src_actor.y - src_actor.atk_target.y < 0:
        src_actor.attempt_move(0, 1)


def turret(src_actor: entities.Actor, game_actors: list[entities.Actor]) -> None:
    pass
