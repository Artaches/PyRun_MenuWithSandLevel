import random, copy, math, os, pygame, sys, player, AI, tiledtmxloader, MENU
from pygame.locals import *

FPS = 30 # frames per second to update the SCREEN
WINWIDTH = 800 # width of the program's window, in pixels
WINHEIGHT = 600 # height in pixels
MOVERATE = 6 # How fast the player moves
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

CAM_MOVE_SPEED = 5 # how many pixels per frame the camera moves

BRIGHTBLUE  = (  0, 170, 255)
WHITE       = (255, 255, 255)
BGCOLOR     = BRIGHTBLUE
TEXTCOLOR   = WHITE

LEFT    = 'left'
RIGHT   = 'right'

TILEMAP_WIDTH = 32
TILEMAP_LENGTH = 24
TILE_SIZE = 25

COLL_LAYER = 2 # The sprite layer which contains the collision map

JUMPING_DURATION = 500      # milliseconds
HORZ_MOVE_INCREMENT = 4     # pixels
TIME_AT_PEAK = JUMPING_DURATION / 2
JUMP_HEIGHT = 100           # pixels




def floorY():
    ''' The Y coordinate of the floor, where the man is placed '''
    return WINHEIGHT - HALF_WINHEIGHT

def jumpHeightAtTime(elapsedTime):
    ''' The height of the jump at the given elapsed time (milliseconds) '''
    return ((-1.0/TIME_AT_PEAK**2)* \
        ((elapsedTime-TIME_AT_PEAK)**2)+1)*JUMP_HEIGHT

'''
    Use this method for blitting images that are suppposed to be partially
    or wholly transparent. Apparently, Python does not provide a good
    method (not even set_alpha(), nor convert()/convert_alpha() in
    conjunction with this works) for blitting these types of images.
    You can have a look here:
    http://www.nerdparadise.com/tech/python/pygame/blitopacity/
'''
def blit_alpha(screenSurface, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pygame.Surface((source.get_width(), source.get_height())).convert()
        temp.blit(screenSurface, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)        
        screenSurface.blit(temp, location)

def makeObstacle(obstacleChoice, position, size, image, direction = 'left'):    
    if (obstacleChoice == 'Giant rock'):
        return AI.soccerBall(position, size, image, direction)
    else:
        return AI.Obstacle((0,0), (0,0), pygame.Surface((0, 0)))
            
    
def main():
    global FPSCLOCK, SCREEN, IMAGESDICT, BASICFONT, PLAYERIMAGES, currentImage
    # Pygame initialization and basic set up of the globalvariables
    pygame.init()
    FPSCLOCK = pygame.time.Clock() # Creates an object to keep track of time.

    SCREEN = pygame.display.set_mode((WINWIDTH, WINHEIGHT))

    pygame.display.set_caption('PyRun')
    BASICFONT = pygame.font.Font('freesansbold.ttf',18)

    # This is a global Dict object (or dictionary object) which
    # contains all of the images that we will use in the game
    IMAGESDICT = {
        'title': pygame.image.load('img/title.png'),
        'player': pygame.image.load('img/run_01.png'),
        'jump1': pygame.image.load('img/jump_01.png'),
        'jump2': pygame.image.load('img/jump_02.png'),
        'jump3': pygame.image.load('img/jump_03.png'),
        'jump4': pygame.image.load('img/jump_04.png'),
        'run1': pygame.image.load('img/run_01.png'),
        'run2': pygame.image.load('img/run_02.png'),
        'run3': pygame.image.load('img/run_03.png'),
        'run4': pygame.image.load('img/run_04.png')
        }    

    # PLAYERIMAGES is a list of all possible characters the player can be.
    # currentImage is the index of the player's current player image.
    currentImage = 0
    # PLAYERIMAGES = [IMAGESDICT['princess']]
    
    Map_Num = startScreen() # function which shows the start menu

    runGame(Map_Num) # run the game



def runGame(MAP_NUMBER):
    '''
        Set up initial player object.    
        This object contains the following keys:
            surface: the image of the player
            facing: the direction the player is facing
            x: the left edge coordinate of the player on the window
            y: the top edge coordinate of the player on the window
            width: the width of the player image
            height: the height of the player image
    '''
    # Initialize the player object
    p = player.Player(
        (HALF_WINWIDTH,HALF_WINHEIGHT),
        (40,100),
        IMAGESDICT['player']
        )
    # For storing our obstacles
    obstacleObjs = []


    # Initialize moving variables
    moveLeft  = False
    moveRight = False
    moveUp    = False
    moveDown  = False


    # parse the level map
    if MAP_NUMBER == 0 :
        level_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode('SandLevel.tmx')
    elif MAP_NUMBER == 1:
        level_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode('testlevel.tmx')

    # load the images using pygame
    resources = tiledtmxloader.helperspygame.ResourceLoaderPygame()
    resources.load(level_map)

    # prepare map rendering
    assert level_map.orientation == "orthogonal"

    # renderer
    renderer = tiledtmxloader.helperspygame.RendererPygame()

    # retrieve the layers
    sprite_layers = tiledtmxloader.helperspygame.get_layers_from_map(resources)

    # filter layers
    sprite_layers = [layer for layer in sprite_layers if not layer.is_object_group]

    # craete player sprite with which we'll work with
    player_sprite = p.get_sprite()

    # add player to the right layer
    sprite_layers[1].add_sprite(player_sprite)

    cam_x = HALF_WINWIDTH
    cam_y = HALF_WINHEIGHT

    # set initial cam position and size
    renderer.set_camera_position_and_size(cam_x, cam_y, WINWIDTH, WINHEIGHT)

    frame_count = 0
    
    while True: # main game loop

        sprite_layers[1].remove_sprite(player_sprite)
        player_sprite = p.get_sprite()
        sprite_layers[1].add_sprite(player_sprite)
        
        # reset applicable variables
        step_x = 0
        step_y = 0

        # This loop will handle all of the player input events
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w, K_SPACE):
                    moveDown = False
                    moveUp = True
                elif event.key in (K_DOWN, K_s):
                    moveUp = False
                    moveDown = True
                elif event.key in (K_LEFT, K_a):
                    moveRight = False
                    moveLeft = True
                elif event.key in (K_RIGHT, K_d):
                    moveLeft = False
                    moveRight = True

            elif event.type == KEYUP:
                # stop moving the player
                if event.key in (K_LEFT, K_a):
                    moveLeft = False
                elif event.key in (K_RIGHT, K_d):
                    moveRight = False
                elif event.key in (K_UP, K_w, K_SPACE):
                    moveUp = False
                elif event.key in (K_DOWN, K_s):
                    moveDown = False            
                elif event.key == K_ESCAPE:
                        terminate()
        '''
            All the jumping and gravity is handled here.
            If the player is jumping we move them up, other wise they are moving down (gravity).
            We can alter how quickly the player jumps by altering the moverate or jump duration.
        '''
        if p.isJumping():
            t = pygame.time.get_ticks() - jumpingStart
            if t > JUMPING_DURATION:
                p.jumping = False
                p.change_sprite(
                IMAGESDICT['jump1']
                )
            elif t > JUMPING_DURATION / 2:
                p.change_sprite(
                IMAGESDICT['jump4']
                )
            step_y -= MOVERATE
        else:
            p.change_sprite(
                IMAGESDICT['jump3']
                )
            step_y += MOVERATE
        
        # actually move the player
        if moveLeft:
            step_x -= MOVERATE
        if moveRight:
            step_x += MOVERATE
            if not p.jumping:
                if frame_count is 20:
                    p.change_sprite(
                    IMAGESDICT['run1']
                    )
                elif frame_count is 40:
                    p.change_sprite(
                    IMAGESDICT['run2']
                    )
                elif frame_count is 60:
                    p.change_sprite(
                    IMAGESDICT['run3']
                    )
                elif frame_count is 80:
                    p.change_sprite(
                    IMAGESDICT['run4']
                    )
                if frame_count > 80:
                    frame_count = 0
        if moveUp:
            if not p.isJumping():
                p.jumping = True
                p.change_sprite(
                IMAGESDICT['jump2']
                )
                jumpingStart = pygame.time.get_ticks()

        step_x, step_y = check_collision(p,step_x,step_y,sprite_layers[COLL_LAYER])

        # Apply the steps to the player and the player rect
        p.x += step_x
        p.y += step_y

        player_sprite.rect.midbottom = (p.x, p.y)        
        
        # Set the new camera position
        renderer.set_camera_position(HALF_WINWIDTH, HALF_WINHEIGHT)

        # Draw the background
        SCREEN.fill((0, 0, 0))

        ''' Collision debugging '''
        # pygame.draw.rect(DISPLAYSURF, (0, 0, 0), (p.x, p.y, p.width, p.height))
        # pygame.draw.rect(DISPLAYSURF, (255, 255, 255), (obstacleObjs[0].xPos, obstacleObjs[0].yPos, obstacleObjs[0].width, obstacleObjs[0].height))
        # pygame.draw.rect(DISPLAYSURF, (255, 0, 255), (obstacleObjs[1].xPos, obstacleObjs[1].yPos, obstacleObjs[1].width, obstacleObjs[1].height))
                    
        
        # render the map including the player
        for sprite_layer in sprite_layers:
            if sprite_layer.is_object_group:
                # we dont draw the object group layers
                # you should filter them out if not needed
                continue
            else:
                renderer.render_layer(SCREEN, sprite_layer)
        
                
        '''
            We need specific drawing cases for different obstacles,
            since every obstacle could have different methods
            defined for drawing executions. This is what we do
            below.
        '''
        '''
            Here, we have backwards-list checking to avoid a common object
            deletion mistake.
        ''' 
        for i in range(len(obstacleObjs) - 1, -1, -1):            
            # Checking if a particular object is a soccer ball.
            if isinstance(obstacleObjs[i], AI.soccerBall):
                obstacleObjs[i].setSpeed(SOCCER_SPEED)
                obstacleObjs[i].doSoccerBallAction(p, floorY() + (p.height/SOCCER_FLOOR_ADJUSTMENT_FACTOR), SOCCER_GRAVITY, WINWIDTH)
                SOCCER_IMG_ROT = pygame.transform.rotate(obstacleObjs[i].image, obstacleObjs[i].soccerBallRotate(SOCCER_ROTATE_INCREMENT))
                SCREEN.blit(SOCCER_IMG_ROT, obstacleObjs[i].get_rect())
            # Checking if a particular object is a banana peel.
            elif isinstance(obstacleObjs[i], AI.bananaPeel):
                obstacleObjs[i].doBananaPeelAction(p, floorY(), SOCCER_GRAVITY, WINWIDTH)
                BANANA_IMG_ROT = pygame.transform.rotate(obstacleObjs[i].image, obstacleObjs[i].slipRotate(floorY(), BANANA_ROTATE_FIRST, BANANA_ROTATE_SECOND))            
                blit_alpha(SCREEN, BANANA_IMG_ROT, obstacleObjs[i].get_rect(), obstacleObjs[i].doFadeOutBananaPeel(BANANA_PEEL_FADE_DECREMENT))
                # Has the banana peel faded to 0 after being slipped on?
                # (This check has been validated)
                if obstacleObjs[i].getBananaPeelFadeAmount() <= 0:                    
                    del obstacleObjs[i]            
            elif isinstance(obstacleObjs[i], AI.spikes):
                obstacleObjs[i].spikeBump(p)
                SCREEN.blit(obstacleObjs[i].image, obstacleObjs[i].get_rect())
                # Default for drawing any other obstacles
            else:
                SCREEN.blit(obstacleObjs[i].image, obstacleObjs[i].get_rect())

        frame_count += 1
        pygame.display.update()
        FPSCLOCK.tick()

def startScreen():
    # Position the title image.
    titleRect = IMAGESDICT['title'].get_rect()
    topCoord = 50 # topCoord track where to position the top of the text
    titleRect.top = topCoord
    titleRect.centerx = HALF_WINWIDTH
    topCoord += titleRect.height



    # Star with drawing a black color to the entire window
    SCREEN.fill(BGCOLOR)

    #Draw the title image to the window:
    SCREEN.blit(IMAGESDICT['title'], (0,0))

    menu = MENU.Menu()#necessary
    menu.set_colors((255,255,255), (0,0,255), (0,255,255))#optional
    menu.set_fontsize(40)#optional
    #menu.set_font('data/couree.fon')#optional
    #menu.move_menu(0, 0)#optional, moves the list of choices BY (x,y)
    menu.init(['Level 1','Level 2','Quit'], SCREEN)#necessary
    #menu.move_menu(0, 0)#optional, moves the choice list TO (x,y)
    menu.draw()#necessary
    
    pygame.key.set_repeat(199,69)#(delay,interval)
    pygame.display.update()
    while 1:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    menu.draw(-1) #here is the Menu class function
                if event.key == K_DOWN:
                    menu.draw(1) #here is the Menu class function
                if event.key == K_RETURN:
                    if menu.get_position() == 0:#here is the Menu class function
                        return 0;
                    elif menu.get_position() == 1:#here is the Menu class function
                        return 1;
                    elif menu.get_position() == 2:#here is the Menu class function
                        pygame.display.quit()
                        sys.exit()
                if event.key == K_ESCAPE:
                    pygame.display.quit()
                    sys.exit()
                pygame.display.update()
            elif event.type == QUIT:
                pygame.display.quit()
                sys.exit()
        pygame.time.wait(8)

    

def check_collision(player,step_x,step_y,coll_layer):
    # find the tile location of the player
    tile_x = int((player.x) // coll_layer.tilewidth)
    tile_y = int((player.y) // coll_layer.tileheight)
    
    # find the tiles around the hero and extract their rects for collision
    tile_rects = []
    for diry in (-1,0, 1):
        for dirx in (-1,0,1):
            if coll_layer.content2D[tile_y + diry][tile_x + dirx] is not None:
                tile_rects.append(coll_layer.content2D[tile_y + diry][tile_x + dirx].rect)

    # save the original steps and return them if not canceled
    res_step_x = step_x
    res_step_y = step_y

    step_x  = special_round(step_x)
    if step_x != 0:
        if player.get_rect().move(step_x, 0).collidelist(tile_rects) > -1:
            res_step_x = 0
    
    # y direction, floor or ceil depending on the sign of the step
    step_y = special_round(step_y)

    # detect a collision and dont move in y direction if colliding
    if player.get_rect().move(0, step_y).collidelist(tile_rects) > -1:
        if player.isJumping() and step_y < 0:
            player.jumping = False;
        res_step_y = 0

    # return the step the hero should do
    return res_step_x, res_step_y

def special_round(value):
    """
    For negative numbers it returns the value floored,
    for positive numbers it returns the value ceiled.
    """
    # same as:  math.copysign(math.ceil(abs(x)), x)
    # OR:
    # ## versus this, which could save many function calls
    # import math
    # ceil_or_floor = { True : math.ceil, False : math.floor, }
    # # usage
    # x = floor_or_ceil[val<0.0](val)

    if value < 0:
        return math.floor(value)
    return math.ceil(value)

    

def terminate():
    pygame.quit()
    sys.exit()

# Checks to see if the file being run is called main, i.e. main.py
# If so it runs the main() function.
if __name__ == '__main__':
    main()
