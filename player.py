import random, copy, os, pygame, sys, tiledtmxloader
from pygame.locals import *

class Player:
    '''
        In order to initialize the player object you must give in the
        position the player will start in, size of the player's image
        and the image that represents the player.

        Both the size and pos paramaters must be ordered pairs. 
        e.g. (0,0), (50,50), etc
    '''	
    def __init__(self,pos,size,image):
        self.image = image
        self.facing = 'right'

        self.x = pos[0]
        self.y = pos[1]
        self.width = size[0]
        self.height = size[1]

        self.onGround = False
        self.jumping = False

        self.rect = self.get_rect()

    def isJumping(self):
        return self.jumping

    def get_rect(self):
        return pygame.Rect((self.x, self.y, self.width, self.height))

    def change_sprite(self,image):
        self.image = image

    def get_sprite(self):
        return tiledtmxloader.helperspygame.SpriteLayer.Sprite(self.image, self.get_rect())

    def get_x_tiles(self):
        '''
            Gets the horizonal tile rows which the player character intersects with
        '''
        topRange = self.y % TILE_SIZE
        bottomRange = (self.y - self.height) % TILE_SIZE

        return (topRange, bottomRange)
