from __future__ import print_function

import os
import sys
import math
import random
import pygame as pg


BACKGROUND_COLOR = (40,40,40)
RECT_SIZE = (30,30)
CAPTION = "Block Collision"


def collide_other(one,two):
    if one is two:
        return False
    else:
        return one.rect.colliderect(two.rect)


class Block(pg.sprite.Sprite):
    def __init__(self,color,position):
        pg.sprite.Sprite.__init__(self)
        self.rect = pg.Rect((0,0),RECT_SIZE)
        self.rect.center = position
        self.image = pg.Surface(self.rect.size).convert()
        self.image.fill(color)
        self.true_pos = list(self.rect.center)
        self.velocity = [random.randint(-5, 5), random.randint(-5, 5)]
        self.unit_vector = self.get_unit_vector(self.velocity)

    def get_unit_vector(self,vector):
        """Return the unit vector of vector."""
        magnitude = math.hypot(*vector)
        if magnitude:
            unit = float(vector[0])/magnitude, float(vector[1])/magnitude
            return unit
        else:
            return 0,0

    def update(self,screen_rect,others):
        """Update position; check collision with other blocks; and check
        collision with screen boundaries."""
        self.before_move = self.rect.copy()##
        self.before_velocity = self.velocity[:]##
        self.true_pos[0] += self.velocity[0]
        self.true_pos[1] += self.velocity[1]
        self.rect.center = self.true_pos
        self.collide_walls(screen_rect)
        self.collide(others)

    def collide_walls(self,screen_rect):
        """Reverse relevent velocity component if colliding with
        edge of screen."""
        out_left = self.rect.left < screen_rect.left
        out_right = self.rect.right > screen_rect.right
        out_top = self.rect.top < screen_rect.top
        out_bottom = self.rect.bottom > screen_rect.bottom
        if out_left or out_right:
            self.velocity[0] *= -1
        if out_top or out_bottom:
            self.velocity[1] *= -1
        if any((out_left,out_right,out_top,out_bottom)):
            self.constrain(screen_rect)
            self.unit_vector = self.get_unit_vector(self.velocity)

    def collide(self,others):
        """Check collision with other and switch components if hit."""
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
                print("Rect: {}, Other: {}".format(self.rect,other.rect))
                print(template.format(**vars(self)))
                print("Unjustly murdered in collide.\n")
                break
        if other:
            on_bottom = self.rect.bottom <= other.rect.top
            on_top = self.rect.top >= other.rect.bottom
            self.switch_components(other,on_bottom or on_top)

    def switch_components(self,other,i):
        """Exchange the i component of velocity with other."""
        self.velocity[i],other.velocity[i] = other.velocity[i],self.velocity[i]
        self.unit_vector = self.get_unit_vector(self.velocity)
        other.unit_vector = other.get_unit_vector(other.velocity)

    def constrain(self,screen_rect):
        """Step back one unit pixel until contained within screen_rect."""
        count = 0
        rect_before = self.rect.copy()
        while not screen_rect.contains(self.rect):
            self.step_back()
            if count > 1000:
                self.kill()
                previous_info = "Before movement: {}, Before velocity: {}"
                rect_info = "Rect before: {}, Rect after: {}"
                print(previous_info.format(self.before_move,self.before_velocity))
                print("Unit: {}".format(self.unit_vector))
                print(rect_info.format(rect_before,self.rect))
                print("Unjustly murdered in constrain.\n")
                break
            count += 1

    def step_back(self):
        """Decrement block's position by one unit pixel."""
        self.true_pos[0] -= self.unit_vector[0]
        self.true_pos[1] -= self.unit_vector[1]
        self.rect.center = self.true_pos


class Control(object):
    def __init__(self):
        pg.init()
        os.environ["SDL_VIDEO_CENTERED"] = "True"
        pg.display.set_caption(CAPTION)
        self.screen = pg.display.set_mode((500,500))
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.blocks = pg.sprite.Group([Block(pg.Color("tomato"),(50,50)),
                                       Block(pg.Color("cyan"),(240,340)),
                                       Block(pg.Color("yellow"),(180,250)),
                                       Block(pg.Color("green"),(35,450))])

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                color = [random.randint(30,255) for _ in range(3)]
                self.blocks.add(Block(color,event.pos))

    def main_loop(self):
        while not self.done:
            self.event_loop()
            self.blocks.update(self.screen_rect,self.blocks)
            self.screen.fill(BACKGROUND_COLOR)
            self.blocks.draw(self.screen)
            pg.display.update()
            self.clock.tick(self.fps)
            now_fps = self.clock.get_fps()
            template = "{} - Blocks: {} - FPS: {:.2f}"
            caption = template.format(CAPTION,len(self.blocks),now_fps)
            pg.display.set_caption(caption)


if __name__ == "__main__":
    Control().main_loop()
    pg.quit()
    sys.exit()
