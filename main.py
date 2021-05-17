import random
import arcade
import timeit
import json
from typing import List
from arcade import *

sprite_scaling = 0.25
sprite_size = 128 * sprite_scaling

screen_width = 670
screen_height = 670
title = "Maze Escape"
speed = 3

tile_empty = 0
tile_brick = 1
sorted_list = []
maze_height = 21
maze_width = 21


def create_maze(maze_width, maze_height):
    maze = []
    for i in range(maze_height):
        maze.append([])
        for j in range(maze_width):
            maze[i].append(1)
    rqueue = []
    cqueue = []
    cqueue.append(1)
    rqueue.append(19)
    maze[19][1] = 0
    while len(cqueue) != 0:
        directions = []
        index = random.randint(0, len(cqueue) - 1)
        currow = rqueue[index]
        curcol = cqueue[index]
        if currow - 2 >= 1:
            if maze[currow - 2][curcol] != 0:
                directions.append(1)
        if currow + 2 <= maze_height - 2:
            if maze[currow + 2][curcol] != 0:
                directions.append(2)
        if curcol - 2 >= 1:
            if maze[currow][curcol - 2] != 0:
                directions.append(3)
        if curcol + 2 <= maze_width - 2:
            if maze[currow][curcol + 2] != 0:
                directions.append(4)
        rand = -1
        if len(directions) > 0:
            rand = random.randint(0, len(directions) - 1)
            rand = directions.pop(rand)
        else:
            rqueue.pop(index)
            cqueue.pop(index)
            rand = -1
        if rand == 1:
            maze[currow - 2][curcol] = 0
            maze[currow - 1][curcol] = 0
            rqueue.append(currow - 2)
            cqueue.append(curcol)
        elif rand == 2:
            maze[currow + 2][curcol] = 0
            maze[currow + 1][curcol] = 0
            rqueue.append(currow + 2)
            cqueue.append(curcol)
        elif rand == 3:
            maze[currow][curcol - 2] = 0
            maze[currow][curcol - 1] = 0
            rqueue.append(currow)
            cqueue.append(curcol - 2)
        elif rand == 4:
            maze[currow][curcol + 2] = 0
            maze[currow][curcol + 1] = 0
            rqueue.append(currow)
            cqueue.append(curcol + 2)
    return maze


class Algorithm:
    def merge_sort(numbers: List[int]) -> List[int]:
        if len(numbers) == 1:
            return numbers
        midpoint = len(numbers) // 2
        left_side = Algorithm.merge_sort(numbers[:midpoint])
        right_side = Algorithm.merge_sort(numbers[midpoint:])
        sorted_list = []
        left_marker = 0
        right_marker = 0
        while left_marker < len(left_side) and right_marker < len(right_side):
            if left_side[left_marker] < right_side[right_marker]:
                sorted_list.append(left_side[left_marker])
                left_marker += 1
            else:
                sorted_list.append(right_side[right_marker])
                right_marker += 1

        while right_marker < len(right_side):
            sorted_list.append(right_side[right_marker])
            right_marker += 1
        while left_marker < len(left_side):
            sorted_list.append(left_side[left_marker])
            left_marker += 1
        return sorted_list


class MenuScreen(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BONE)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("LOCKDOWN", screen_width / 2, screen_height - 100,
                         arcade.color.TEAL, font_size=50, anchor_x="center")
        arcade.draw_text("You wake up in your office and realize there is a zombie apocalypse.",
                         screen_width / 2, screen_height - 200, arcade.color.TEAL, font_size=12, anchor_x="center")
        arcade.draw_text("Get out of the building with three floors to get to the nearest safe zone",
                         screen_width / 2, screen_height - 250, arcade.color.TEAL, font_size=12, anchor_x="center")
        arcade.draw_text("Controls:",
                         screen_width / 2, screen_height - 300, arcade.color.TEAL, font_size=12, anchor_x="center")
        arcade.draw_text("W - Up",
                         screen_width / 2, screen_height / 2, arcade.color.TEAL, font_size=12, anchor_x="center")
        arcade.draw_text("S - Down",
                         screen_width / 2, screen_height / 2 - 50, arcade.color.TEAL, font_size=12, anchor_x="center")
        arcade.draw_text("A - Left",
                         screen_width / 2, screen_height / 2 - 100, arcade.color.TEAL, font_size=12, anchor_x="center")
        arcade.draw_text("D - Right",
                         screen_width / 2, screen_height / 2 - 150, arcade.color.TEAL, font_size=12, anchor_x="center")
        arcade.draw_text("Click to start game",
                         screen_width / 2, screen_height / 2 - 200, arcade.color.TEAL, font_size=12, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        maze = Maze()
        maze.setup()
        self.window.show_view(maze)


class Maze(arcade.View):
    def __init__(self):
        super().__init__()
        self._player_list = arcade.SpriteList()
        self._wall_list = arcade.SpriteList()
        self._staircase_list = arcade.SpriteList()
        self._player_sprite = arcade.Sprite("images/persone.png", sprite_scaling)
        self._player_list.append(self._player_sprite)
        self._staircase_sprite = arcade.Sprite("images/staircase.jpg", sprite_scaling)
        self._staircase_list.append(self._staircase_sprite)
        self._counter = 0
        self._time = 0
        self._movement_queue = []

    def on_show(self):
        arcade.set_background_color(arcade.color.BONE)

    def setup(self):
        self._wall_list = arcade.SpriteList()
        self._physics_engine = PhysicsEngineSimple(self._player_sprite, self._wall_list)
        maze = create_maze(maze_width, maze_height)
        for row in range(maze_height):
            for column in range(maze_width):
                if maze[row][column] == 1:
                    wall = arcade.Sprite("images/brick.png", sprite_scaling)
                    wall.center_x = column * sprite_size + sprite_size / 2
                    wall.center_y = row * sprite_size + sprite_size / 2
                    self._wall_list.append(wall)
        placed = False
        self._player_sprite.center_x = 50
        self._player_sprite.center_y = 50
        walls_hit = arcade.check_for_collision_with_list(self._player_sprite, self._wall_list)
        if len(walls_hit) == 0:
            placed = True
        self._staircase_sprite.center_x = 625
        self._staircase_sprite.center_y = 625
        walls_hit = arcade.check_for_collision_with_list(self._staircase_sprite, self._wall_list)
        if len(walls_hit) == 0:
            placed = True

    def on_draw(self):
        arcade.start_render()
        self._wall_list.draw()
        self._player_list.draw()
        self._staircase_list.draw()
        output = f"Time: {self._time:.3f} seconds"
        arcade.draw_text(output, 20, screen_height - 20, arcade.color.WHITE, 16)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W:
            self._movement_queue.insert(0, 'u')
        elif key == arcade.key.S:
            self._movement_queue.insert(0, 'd')
        elif key == arcade.key.A:
            self._movement_queue.insert(0, 'l')
        elif key == arcade.key.D:
            self._movement_queue.insert(0, 'r')

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W:
            self._movement_queue.remove('u')
        elif key == arcade.key.S:
            self._movement_queue.remove('d')
        elif key == arcade.key.A:
            self._movement_queue.remove('l')
        elif key == arcade.key.D:
            self._movement_queue.remove('r')

    def on_update(self, delta_time):
        self._wall_list.update()
        self._player_list.update()
        self._staircase_list.update()
        self._physics_engine.update()

        if len(self._movement_queue) > 0:
            if self._movement_queue[0] == 'u':
                self._player_sprite.change_y = speed
                self._player_sprite.change_x = 0
            elif self._movement_queue[0] == 'd':
                self._player_sprite.change_y = -speed
                self._player_sprite.change_x = 0
            elif self._movement_queue[0] == 'l':
                self._player_sprite.change_x = -speed
                self._player_sprite.change_y = 0
            elif self._movement_queue[0] == 'r':
                self._player_sprite.change_x = speed
                self._player_sprite.change_y = 0
        else:
            self._player_sprite.change_y = 0
            self._player_sprite.change_x = 0
        self._time += delta_time

        for player in self._player_list:
            hit_list = arcade.check_for_collision_with_list(player, self._staircase_list)

        for player in hit_list:
            self.setup()
            self._counter += 1

            if self._counter == 3:
                global time
                time = self._time
                escaped_building = EscapedBuilding()
                self.window.show_view(escaped_building)


class EscapedBuilding(arcade.View):
    def on_draw(self):
        arcade.start_render()
        maze_time = round(time, 2)
        arcade.draw_text(f"You Escaped The Building In {maze_time} Seconds",
                         screen_width / 2, screen_height / 2, arcade.color.TEAL, font_size=20, anchor_x="center")

    def on_show(self):
        arcade.set_background_color(arcade.color.BONE)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        maze_time = round(time, 2)

        with open("time.json", "r") as f:
            data = json.load(f)

        data[f"time {len(data) + 1}"] = maze_time

        with open("time.json", 'w') as f:
            json.dump(data, f)

        highscores = Highscores()
        self.window.show_view(highscores)


class Highscores(arcade.View):

    @classmethod
    def on_show(cls):
        arcade.set_background_color(arcade.color.BONE)

    @classmethod
    def on_draw(cls):
        arcade.start_render()
        maze_time = round(time, 2)
        height_decrease = 120
        sorted_list = []
        with open("time.json", "r") as f:
            data = json.load(f)

        for values in data.values():
            sorted_list.append(values)
            sorted_list2 = Algorithm.merge_sort(sorted_list)

        arcade.draw_text(f"Shortest Times: \n",
                         screen_width / 2, screen_height - 200, arcade.color.TEAL, font_size=18, anchor_x="center")

        if len(sorted_list2) < 5:
            for i in reversed(range(0, len(sorted_list2))):
                arcade.draw_text(f"{i + 1}: {sorted_list2[i]} \n",
                                 screen_width / 2, screen_height - 200 - height_decrease,
                                 arcade.color.TEAL, font_size=18, anchor_x="center")
                height_decrease -= 20
        else:
            for i in reversed(range(0, 5)):
                arcade.draw_text(f"{i + 1}: {sorted_list2[i]} \n",
                                 screen_width / 2, screen_height - 200 - height_decrease,
                                 arcade.color.TEAL, font_size=18, anchor_x="center")
                height_decrease -= 20

        arcade.draw_text(f"Your Time: {maze_time}", screen_width / 2, screen_height / 2 - 100,
                         arcade.color.TEAL, font_size=18, anchor_x="center")
        arcade.draw_text(f"Click to play again", screen_width / 2, screen_height / 2 - 250,
                         arcade.color.TEAL, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        window = MenuScreen()
        self.window.show_view(window)


class PhysicsEngineSimple:
    def __init__(self, player_sprite, walls):
        self._player_sprite = player_sprite
        self._walls = walls

        def get_player_sprite(self):
            return self._player_sprite

        def set_player_sprite(self, value):
            self._player_sprite = value

        def get_walls(self):
            return self._walls

        def set_walls(self, value):
            self._walls = value

    def update(self):
        self._player_sprite.center_x += self._player_sprite.change_x
        hit_list_x = \
            check_for_collision_with_list(self._player_sprite, self._walls)
        if len(hit_list_x) > 0:
            if self._player_sprite.change_x > 0:
                for item in hit_list_x:
                    self._player_sprite.right = min(item.left, self._player_sprite.right)
            elif self._player_sprite.change_x < 0:
                for item in hit_list_x:
                    self._player_sprite.left = max(item.right, self._player_sprite.left)

        self._player_sprite.center_y += self._player_sprite.change_y

        hit_list_y = \
            check_for_collision_with_list(self._player_sprite, self._walls)

        if len(hit_list_y) > 0:
            if self._player_sprite.change_y > 0:
                for item in hit_list_y:
                    self._player_sprite.top = min(item.bottom, self._player_sprite.top)
            else:
                for item in hit_list_y:
                    self._player_sprite.bottom = max(item.top, self._player_sprite.bottom)

        complete_hit_list = hit_list_x
        for sprite in hit_list_y:
            complete_hit_list.append(sprite)
        return complete_hit_list

def main():
    window = arcade.Window(screen_width, screen_height, title)
    menu_screen = MenuScreen()
    window.show_view(menu_screen)
    arcade.run()


if __name__ == "__main__":
    main()
