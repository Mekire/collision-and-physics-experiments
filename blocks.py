from __future__ import print_function

import os
import sys
import math
import random
import pygame as pg


BACKGROUND_COLOR = (30, 40, 50)
SCREEN_SIZE = (700, 500)
RECT_SIZE = (50, 50)
CAPTION = "Block Collision"

START_BLOCKS = [(pg.Color("tomato"), (50,50)), (pg.Color("cyan"), (240,340)),
                (pg.Color("yellow"), (180,250)), (pg.Color("green"), (35,450))]


def collide_other(one, two):
    """
    Callback function for use with pg.sprite.collidesprite methods.
    It simply allows a sprite to test collision against its own group,
    without returning false positives with itself.
    """
    return one is not two and pg.sprite.collide_rect(one, two)


class Block(pg.sprite.Sprite):
    """Our basic bouncing block."""
    def __init__(self, color, position):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface(RECT_SIZE).convert()
        self.image.fill(color)
        self.rect = self.image.get_rect(center=position)
        self.true_pos = list(self.rect.center)
        self.velocity = [random.randint(-5, 5), random.randint(-5, 5)]
        self.unit_vector = self.get_unit_vector(self.velocity)

    def get_unit_vector(self, vector):
        """Return the unit vector of vector."""
        magnitude = math.hypot(*vector)
        if magnitude:
            return float(vector[0])/magnitude, float(vector[1])/magnitude
        else:
            return (0, 0)

    def update(self, screen_rect, others):
        """
        Update position; check collision with other blocks; and check
        collision with screen boundaries.
        """
        self.before_move = self.rect.copy()
        self.before_vel = self.velocity[:]
        self.true_pos[0] += self.velocity[0]
        self.true_pos[1] += self.velocity[1]
        self.rect.center = self.true_pos
        self.collide_walls(screen_rect)
        self.collide(others)

    def collide_walls(self, screen_rect):
        """
        Reverse relevent velocity component if colliding with edge of screen.
        """
        out_left = self.rect.left < screen_rect.left
        out_right = self.rect.right > screen_rect.right
        out_top = self.rect.top < screen_rect.top
        out_bottom = self.rect.bottom > screen_rect.bottom
        if out_left or out_right:
            self.velocity[0] *= -1
        if out_top or out_bottom:
            self.velocity[1] *= -1
        if any([out_left, out_right, out_top, out_bottom]):
            self.constrain(screen_rect)
            self.unit_vector = self.get_unit_vector(self.velocity)

    def collide(self, others):
        """
        Check collision with other and switch components if hit.
        If collision can not be rectified, block is auto-killed.
        """
        count = 0
        other = None
        hit = pg.sprite.spritecollideany(self, others, collide_other)
        while hit:
            other = hit
            self.step_back()
            hit = pg.sprite.spritecollideany(self, others, collide_other)
            count += 1
            if count > 1000:
                self.kill()
                template = "Velocity: {velocity}, Unit: {unit_vector}"
                print("Rect: {}, Other: {}".format(self.rect, other.rect))
                print(template.format(**vars(self)))
                print("Unjustly murdered in collide.\n")
                break
        if other:
            on_bottom = self.rect.bottom <= other.rect.top
            on_top = self.rect.top >= other.rect.bottom
            self.switch_components(other,on_bottom or on_top)

    def switch_components(self, other, i):
        """Exchange the i component of velocity with other."""
        self.velocity[i],other.velocity[i] = other.velocity[i],self.velocity[i]
        self.unit_vector = self.get_unit_vector(self.velocity)
        other.unit_vector = other.get_unit_vector(other.velocity)

    def constrain(self, screen_rect):
        """
        Step back one unit pixel until contained within screen_rect.
        If the block is not contained within the screen after a number of
        iterations, it will be automaticaly killed.
        """
        count = 0
        rect_before = self.rect.copy()
        while not screen_rect.contains(self.rect):
            self.step_back()
            if count > 1000:
                self.kill()
                previous_info = "Before movement: {}, Before velocity: {}"
                rect_info = "Rect before: {}, Rect after: {}"
                print(previous_info.format(self.before_move, self.before_vel))
                print("Unit: {}".format(self.unit_vector))
                print(rect_info.format(rect_before, self.rect))
                print("Unjustly murdered in constrain.\n")
                break
            count += 1

    def step_back(self):
        """Decrement block's position by one unit pixel."""
        self.true_pos[0] -= self.unit_vector[0]
        self.true_pos[1] -= self.unit_vector[1]
        self.rect.center = self.true_pos


class Control(object):
    """The big boss."""
    def __init__(self):
        pg.init()
        os.environ["SDL_VIDEO_CENTERED"] = "True"
        pg.display.set_caption(CAPTION)
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.blocks = pg.sprite.Group(Block(*args) for args in START_BLOCKS)

    def event_loop(self):
        """Add blocks on mouse click."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                color = [random.randint(30,255) for _ in range(3)]
                self.blocks.add(Block(color,event.pos))

    def draw(self):
        """Fill the screen and draw all blocks."""
        self.screen.fill(BACKGROUND_COLOR)
        self.blocks.draw(self.screen)

    def display_fps(self):
        """Update the caption with the new fps (and block count)."""
        self.clock.tick(self.fps)
        now_fps = self.clock.get_fps()
        template = "{} - Blocks: {} - FPS: {:.2f}"
        caption = template.format(CAPTION, len(self.blocks), now_fps)
        pg.display.set_caption(caption)

    def main_loop(self):
        """Run in circles."""
        while not self.done:
            self.event_loop()
            self.blocks.update(self.screen_rect, self.blocks)
            self.draw()
            pg.display.update()
            self.display_fps()


if __name__ == "__main__":
    Control().main_loop()
    pg.quit()
    sys.exit()
