from __future__ import annotations
import math
import time
from typing import Optional, Any
import databases
import interface
import entities
import bresenham
import rendering


class Entity:
    """Represents any game entity."""

    def __init__(
            self,
            x: int,
            y: int,
            name: str,
            desc: str,
            blocked: bool,
            graphic: str,
            color: Optional[tuple[int, int, int]],
            game_data: databases.Databases,
            game_entities_: entities.GameEntities,
            game_interface: interface.Interface,
            cover_percent: int = 0,
            visible: bool = True
    ) -> None:
        self.x: int = x
        self.y: int = y
        self.name: str = name
        self.desc: str = desc
        self.old_graphic = graphic
        self.graphic: str = graphic
        self.color: Optional[tuple[int, int, int]] = color
        self.bgcolor: Optional[tuple[int, int, int]] = None
        self.blocked: bool = blocked
        self.old_visible: bool = visible
        self.visible: bool = visible
        self.noise_level: int = 0
        self.cover_percent = cover_percent

        self.game_data: databases.Databases = game_data
        self.game_interface: interface.Interface = game_interface
        self.game_entities: entities.GameEntities = game_entities_

        game_entities_.all.append(self)

    def render(self, surface: Any) -> None:
        """Renders the entity."""

        if self.visible:
            rendering.render(surface, self.graphic, self.x, self.y, self.color, self.bgcolor)

    def update(self, game_time: int) -> None:
        """Updates the entity."""
        pass

    def remove(self) -> None:
        """Removes the entity from the list of all entities."""

        for entity_ in enumerate(self.game_entities.all):
            if entity_[1] is self:
                self.game_entities.all.pop(entity_[0])

    def make_noise(self, noise_radius: int) -> None:
        """Causes this entity to make noise."""
        self.noise_level = noise_radius

    def highlight(self, color: Optional[tuple[int, int, int]]):
        """Highlights this entity by setting it's background color.
           If the tile is invisible, do some stuff to still get a highlight of it."""

        self.bgcolor = color

        if self.visible:
            if color is None:
                self.visible = self.old_visible
                self.graphic = self.old_graphic
        else:
            if color is not None:
                self.old_visible = self.visible
                self.old_graphic = self.graphic
                self.graphic = ' '
                self.visible = True

    def get_line_of_sight(
            self,
            x2: int,
            y2: int,
            extend: bool = False,
            ignore_cover: bool = True
    ) -> list[tuple[int, int]]:
        """Uses the bresenham line algorithm to get a list of points on the map the LOS would pass through."""

        end_x: int = x2
        end_y: int = y2

        # Extend the path beyond where entity selected using slope of line.
        if extend:
            end_x = x2 + ((x2 - self.x) * 20)  # 20 is arbitrary number for max LOS range.
            end_y = y2 + ((y2 - self.y) * 20)

        # Disclude the entity from the LOS.
        los: list[tuple[int, int]] = bresenham.bresenham((self.x, self.y), (end_x, end_y))[1:]

        # Check each point in the LOS if it's 100% cover (basically meaning it's a wall). If so, stop the LOS there.
        final_los: list[tuple[int, int]] = []
        for point in los:
            final_los.append(point)
            for entity in self.game_entities.get_all_at(point[0], point[1]):
                if entity.cover_percent == 100 or (not ignore_cover and entity.blocked):
                    return final_los

        return final_los

    def render_projectile(
            self,
            points: list[tuple[int, int]],
            char: str,
            color: tuple[int, int, int],
            delay: float
    ) -> None:
        """'Animates' a projectile as it flies through the air by sleeping briefly between renders."""

        self.game_entities.render_all(self.game_entities.surface)
        for point in points:
            rendering.render(self.game_entities.surface, char, point[0], point[1], color)
        self.game_entities.window.present(self.game_entities.surface)
        time.sleep(delay)

    def compute_fov(self, radius: int, ignore_cover: bool = True) -> list[tuple[int, int]]:
        """Computes all seeable points in a radius from the entity by casting a line along the circumference
        of the radius and seeing if the line hits any blocked objects."""

        top: int = self.y - radius
        bottom: int = self.y + radius
        left: int = self.x - radius
        right: int = self.x + radius

        # Gets each point along the circumference of the circle formed by the radius
        circ_points: list[tuple[int, int]] = []
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                distance: float = math.dist((x, y), (self.x, self.y))

                if 0.0 <= (radius - distance) < 1.0:
                    circ_points.append((x, y))

        # Now calculate the line-of-sight to each point along the circumference to check if anything is blocking view
        fov: list[tuple[int, int]] = []
        for circ_point in circ_points:
            los: list[tuple[int, int]] = self.get_line_of_sight(circ_point[0], circ_point[1], False, ignore_cover)
            for los_point in los:
                fov.append(los_point)

        return fov
