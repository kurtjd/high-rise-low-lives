from __future__ import annotations
import game_entities.actor


def smart_melee(src_actor: game_entities.actor.Actor, game_actors: list[game_entities.actor.Actor]) -> None:
    """ For intelligent actors that like to fight up-close and personal.
    This is basic, temporary AI. """

    # If not currently targeting an actor, find the player for now.
    if src_actor.atk_target is None:
        for entity in game_actors:
            if isinstance(entity, game_entities.actor.Player):
                src_actor.atk_target = entity
                break

    did_move: bool
    # Simply attempt to move toward target, and stepping onto target attacks it.
    if src_actor.x - src_actor.atk_target.x > 0:
        did_move = src_actor.attempt_move(-1, 0)
        if not did_move:
            src_actor.attempt_move(0, 1)
    elif src_actor.x - src_actor.atk_target.x < 0:
        did_move = src_actor.attempt_move(1, 0)
        if not did_move:
            src_actor.attempt_move(0, 1)
    if src_actor.y - src_actor.atk_target.y > 0:
        did_move = src_actor.attempt_move(0, -1)
        if not did_move:
            src_actor.attempt_move(1, 0)
    elif src_actor.y - src_actor.atk_target.y < 0:
        did_move = src_actor.attempt_move(0, 1)
        if not did_move:
            src_actor.attempt_move(1, 0)


def smart_ranged(src_actor: game_entities.actor.Actor, game_actors: list[game_entities.actor.Actor]) -> None:
    """ For intelligent actors that like to fight from a distance.
    This is basic, temporary AI. """

    # If not currently targeting an actor, find the player for now.
    if src_actor.atk_target is None:
        for entity in game_actors:
            if isinstance(entity, game_entities.actor.Player):
                src_actor.atk_target = entity
                break

    did_move: bool = False
    # Simply attempt to move within range of target, and fire if close enough.
    if src_actor.x - src_actor.atk_target.x > 5:
        did_move = src_actor.attempt_move(-1, 0)
        if not did_move:
            src_actor.attempt_move(0, 1)
    elif src_actor.x - src_actor.atk_target.x < 5:
        did_move = src_actor.attempt_move(1, 0)
        if not did_move:
            src_actor.attempt_move(0, 1)
    if src_actor.y - src_actor.atk_target.y > 5:
        did_move = src_actor.attempt_move(0, -1)
        if not did_move:
            src_actor.attempt_move(1, 0)
    elif src_actor.y - src_actor.atk_target.y < 5:
        did_move = src_actor.attempt_move(0, 1)
        if not did_move:
            src_actor.attempt_move(1, 0)

    if abs(src_actor.x - src_actor.atk_target.x) <= 5 and abs(src_actor.y - src_actor.atk_target.y) <= 5:
        bullet_path = src_actor.get_line_of_sight(src_actor.atk_target.x, src_actor.atk_target.y, True)
        src_actor.attempt_atk(src_actor.atk_target.x, src_actor.atk_target.y, True, bullet_path)
    elif not did_move:
        src_actor.attempt_rest()


def turret(src_actor: game_entities.actor.Actor, game_actors: list[game_entities.actor.Actor]) -> None:
    """ For all stationary turrets.
    This is basic, temporary AI. """

    # If not currently targeting an actor, find the player for now.
    if src_actor.atk_target is None:
        for entity in game_actors:
            if isinstance(entity, game_entities.actor.Player):
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

        src_actor.bullet_path = src_actor.get_line_of_sight(src_actor.atk_target.x, src_actor.atk_target.y, True)
        src_actor.attempt_atk(atk_x, atk_y, True, src_actor.bullet_path)
    else:
        src_actor.attempt_rest()
