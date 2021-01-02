import entities


# Each Actor carries a reference to one of these AI functions depending on its abilities and style.

# For intelligent actors that like to fight up-close and personal.
def smart_melee(src_actor: "entities.Actor", game_actors: list["entities.Actor"]) -> None:
    # If not currently targeting an actor, find the player for now.
    if src_actor.atk_target is None:
        for entity in game_actors:
            if entity.is_player:
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


def smart_ranged(src_actor: "entities.Actor", game_actors: list["entities.Actor"]) -> None:
    # If not currently targeting an actor, find the player for now.
    if src_actor.atk_target is None:
        for entity in game_actors:
            if entity.is_player:
                src_actor.atk_target = entity
                break

    # Simply attempt to move within range of target, and fire if close enough.
    if src_actor.x - src_actor.atk_target.x > 5:
        src_actor.attempt_move(-1, 0)
    elif src_actor.x - src_actor.atk_target.x < 5:
        src_actor.attempt_move(1, 0)
    if src_actor.y - src_actor.atk_target.y > 5:
        src_actor.attempt_move(0, -1)
    elif src_actor.y - src_actor.atk_target.y < 5:
        src_actor.attempt_move(0, 1)

    if abs(src_actor.x - src_actor.atk_target.x) <= 5 and abs(src_actor.y - src_actor.atk_target.y) <= 5:
        src_actor.set_bullet_path(src_actor.atk_target.x, src_actor.atk_target.y)
        src_actor.attempt_atk(src_actor.atk_target.x, src_actor.atk_target.y, True, src_actor.bullet_path)


def turret(src_actor: "entities.Actor", game_actors: list["entities.Actor"]) -> None:
    # If not currently targeting an actor, find the player for now.
    if src_actor.atk_target is None:
        for entity in game_actors:
            if entity.is_player:
                src_actor.atk_target = entity
                break

    # Fix target prediction.
    if abs(src_actor.atk_target.x - src_actor.x) < 5 and abs(src_actor.atk_target.y - src_actor.y) < 5:
        atk_x: int
        atk_y: int
        if src_actor.atk_target.dest_x == 0:
            atk_x = src_actor.atk_target.x
        else:
            atk_x = src_actor.atk_target.dest_x

        if src_actor.atk_target.dest_y == 0:
            atk_y = src_actor.atk_target.y
        else:
            atk_y = src_actor.atk_target.dest_y

        print(f"Player: ({src_actor.atk_target.x}, {src_actor.atk_target.y})")
        print(f"Target: ({atk_x}, {atk_y})")

        src_actor.set_bullet_path(src_actor.atk_target.x, src_actor.atk_target.y)
        src_actor.attempt_atk(atk_x, atk_y, True, src_actor.bullet_path)
    else:
        src_actor.attempt_rest()
