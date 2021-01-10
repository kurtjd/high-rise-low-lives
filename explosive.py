from __future__ import annotations
import entities
import databases
import interface
import entity
import actor


class Explosive(entity.Entity):
    """Represents an explosive on the map before and after it goes off."""

    def __init__(
            self,
            x: int,
            y: int,
            damage: int,
            blast_radius: int,
            fuse: int,
            game_data: databases.Databases,
            game_entities_: entities.GameEntities,
            game_interface: interface.Interface
    ) -> None:
        tile_: dict = game_data.tiles["EXPLOSIVE"]

        super().__init__(
            x,
            y,
            tile_["Name"],
            tile_["Desc"],
            tile_["Blocked"],
            tile_["Character"],
            tile_["Color"],
            game_data,
            game_entities_,
            game_interface
        )

        self.fuse = fuse  # How many rounds before going off.
        self.damage = damage
        self.blast_radius = blast_radius

        game_entities_.explosives.append(self)

    def explode(self) -> None:
        """Called after the fuse has run out and unleashes an explosion."""

        actors_hit: list[actor.Actor] = []  # Used to keep track of actors receiving damage so they don't get hit twice.

        # Grows the explosion out to its max blast radius.
        for i in range(self.blast_radius + 1):
            blast_zone: list[tuple[int, int]]
            if i == 0:
                # The explosion is directly under an actor.
                blast_zone = [(self.x, self.y)]
            else:
                blast_zone = self.compute_fov(i, False)

            # Check each point in the blast zone to see if it hit an actor.
            for point in blast_zone:
                actor_: actor.Actor = self.game_entities.get_actor_at(point[0], point[1])
                if actor_ is not None and actor_.health >= 0 and actor_ not in actors_hit:
                    actor_.receive_hit(self, round(self.damage / (i + 1)), 100)
                    actors_hit.append(actor_)

            self.render_projectile(blast_zone, '*', self.game_data.colors["RED"], 0.05)

        self.remove()

    def update(self, game_time: int) -> None:
        """Updates the explosive."""

        # Decrease the fuse every round.
        self.fuse -= 1
        if self.fuse <= 0:
            self.explode()

    def remove(self) -> None:
        """Removes the explosive from the list of all explosives."""

        explosives: list[Explosive] = self.game_entities.explosives
        for explosive_ in enumerate(explosives):
            if explosive_[1] is self:
                explosives.pop(explosive_[0])

        super().remove()
