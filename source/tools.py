import pygame, sys, time
from pygame.locals import *

#Set up window resolution
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
#WINDOW_WIDTH = 1920
#WINDOW_HEIGHT = 1080
FPS = 40
#Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
BROWN = (165, 42, 42)
#Game directories
LAND_TILES_DIR = 'tiles\\'
SPRITES_DIR =    'sprite\\'
SCENARIO_DIR =   'scenario\\'
CONTROLS_DIR =   'controls\\'
#Number of cells by X and Y axises
LAND_NUM_Y = 4
LAND_NUM_X = 6
#Timing and delay intervals
SEND_INTERVAL = 700
#Land cell types
FIELD =     'field'
FOREST =    'forest'
MOUNTAIN =  'mountain'
WATER =     'water'
CAMP =      'camp'
#Side(control) panel and game field width
SIDE_PANEL_WIDTH = WINDOW_WIDTH - WINDOW_HEIGHT // LAND_NUM_Y * LAND_NUM_X
FIELD_WIDTH = WINDOW_WIDTH - SIDE_PANEL_WIDTH
#Cell width and height
LAND_CELL_HEIGHT = WINDOW_HEIGHT // LAND_NUM_Y
LAND_CELL_WIDTH = LAND_CELL_HEIGHT
#Movement direction constants
DOWN_LEFT  = 1
DOWN       = 2
DOWN_RIGHT = 3
LEFT       = 4
RIGHT      = 6
UP_LEFT    = 7
UP         = 8
UP_RIGHT   = 9
#Resource richness in land cell
EMPTY =     'empty'
LOW =       'low'
MODERATE =  'moderate'
MANY =      'many'
RICH =      'rich'
#Resource types
FOOD =          'food'
STOCKED_FOOD =  'stocked_food'
HIDDEN_BONES =  'hidden_bones'
BONES =         'bones'
MOIST_SKIN =    'moist_skin'
SKIN =          'skin'
WOOD =          'wood'
STONE =         'stone'

def main():
    constants = {}
    output_list= []
    
    constants['WINDOW_WIDTH']       = str(WINDOW_WIDTH)
    constants['WINDOW_HEIGHT']      = str(WINDOW_HEIGHT)
    constants['FPS']                = str(FPS)
    constants['RED']                = str(RED)
    constants['GREEN']              = str(GREEN)
    constants['ORANGE']             = str(ORANGE)
    constants['BROWN']              = str(BROWN)
    constants['LAND_TILES_DIR']     = str(LAND_TILES_DIR)
    constants['SPRITES_DIR']        = str(SPRITES_DIR)
    constants['SCENARIO_DIR']       = str(SCENARIO_DIR)
    constants['CONTROLS_DIR']       = str(CONTROLS_DIR)
    constants['LAND_NUM_Y']         = str(LAND_NUM_Y)
    constants['LAND_NUM_X']         = str(LAND_NUM_X)
    constants['SEND_INTERVAL']      = str(SEND_INTERVAL)
    constants['FIELD']              = str(FIELD)
    constants['FOREST']             = str(FOREST)
    constants['MOUNTAIN']           = str(MOUNTAIN)
    constants['WATER']              = str(WATER)
    constants['CAMP']               = str(CAMP)
    constants['SIDE_PANEL_WIDTH']   = str(SIDE_PANEL_WIDTH)
    constants['FIELD_WIDTH']        = str(FIELD_WIDTH)
    constants['LAND_CELL_HEIGHT']   = str(LAND_CELL_HEIGHT)
    constants['DOWN_LEFT']          = str(DOWN_LEFT)
    constants['DOWN']               = str(DOWN)
    constants['DOWN_RIGHT']         = str(DOWN_RIGHT)
    constants['LEFT']               = str(LEFT)
    constants['RIGHT']              = str(RIGHT)
    constants['UP_LEFT']            = str(UP_LEFT)
    constants['UP']                 = str(UP)
    constants['UP_RIGHT']           = str(UP_RIGHT)
    constants['EMPTY']              = str(EMPTY)
    constants['LOW']                = str(LOW)
    constants['MODERATE']           = str(MODERATE)
    constants['MANY']               = str(MANY)
    constants['RICH']               = str(RICH)
    constants['FOOD']               = str(FOOD)
    constants['STOCKED_FOOD']       = str(STOCKED_FOOD)
    constants['HIDDEN_BONES']       = str(HIDDEN_BONES)
    constants['BONES']              = str(BONES)
    constants['MOIST_SKIN']         = str(MOIST_SKIN)
    constants['SKIN']               = str(SKIN)
    constants['WOOD']               = str(WOOD)
    constants['STONE']              = str(STONE)

    output_list.append('\nSet up window resolution')
    output_list.append('WINDOW_WIDTH')
    output_list.append('WINDOW_HEIGHT')
    output_list.append('FPS')
    output_list.append('\nSet up window resolution')
    output_list.append('RED')
    output_list.append('GREEN')
    output_list.append('ORANGE')
    output_list.append('BROWN')
    output_list.append('\nGame directories')
    output_list.append('LAND_TILES_DIR')
    output_list.append('SPRITES_DIR')
    output_list.append('SCENARIO_DIR')
    output_list.append('CONTROLS_DIR')
    output_list.append('\nNumber of cells by X and Y axises')
    output_list.append('LAND_NUM_Y')
    output_list.append('LAND_NUM_X')
    output_list.append('\nTiming and delay intervals')
    output_list.append('SEND_INTERVAL')
    output_list.append('\nLand cell types')
    output_list.append('FIELD')
    output_list.append('FOREST')
    output_list.append('MOUNTAIN')
    output_list.append('WATER')
    output_list.append('CAMP')
    output_list.append('\nSide(control) panel and game field width')
    output_list.append('SIDE_PANEL_WIDTH')
    output_list.append('FIELD_WIDTH')
    output_list.append('\nCell width and height')
    output_list.append('LAND_CELL_HEIGHT')
    output_list.append('\nMovement direction constants')
    output_list.append('DOWN_LEFT')
    output_list.append('DOWN')
    output_list.append('DOWN_RIGHT')
    output_list.append('LEFT')
    output_list.append('RIGHT')
    output_list.append('UP_LEFT')
    output_list.append('UP')
    output_list.append('UP_RIGHT')
    output_list.append('\nResource richness in land cell')
    output_list.append('EMPTY')
    output_list.append('LOW')
    output_list.append('MODERATE')
    output_list.append('MANY')
    output_list.append('RICH')
    output_list.append('\nResource types')
    output_list.append('FOOD')
    output_list.append('STOCKED_FOOD')
    output_list.append('HIDDEN_BONES')
    output_list.append('BONES')
    output_list.append('MOIST_SKIN')
    output_list.append('SKIN')
    output_list.append('MANY')
    output_list.append('WOOD')
    output_list.append('STONE')

    file=open('..//setup.ini', 'w')
    for item in output_list:
        if item in constants:
            file.write(item + '=' + constants[item] + '\n')
        else:
            file.write(item + '\n')
    file.close()

def importConstants():
    '''
    (None) -> dict

    Imports all constants from setup.ini file and returns them as a dictionary where
    key is a constant name and value is a constant value
    '''
    constants = {}
    setup=open('setup.ini', 'r')
    for line in setup:
        if '=' in line:
            name,value = line.split('=')
            # If value is a number
            if value[:-1].isnumeric():
                value = int(value)

            # If value is a Tuple
            elif value[0] == '(' and value[-2] == ')':
                tuple_builder = value[1:-2].split(', ')
                for element in range(0,len(tuple_builder)):
                    if tuple_builder[element].isnumeric():
                        tuple_builder[element] = int(tuple_builder[element])
                value = tuple_builder

            # If value is a string
            else:
                value = value[:-1]
            constants[name] = value
    return constants

def drawNet(ScreenSurface):
    '''
    (Surface) -> None

    Draws net on the edge of cells
    '''
    
    #drawing Y lines
    for y in range(0, LAND_NUM_Y):
        pygame.draw.line(ScreenSurface, RED, (0, y*LAND_CELL_HEIGHT),\
                        (FIELD_WIDTH, y*LAND_CELL_HEIGHT))
        
    #drawing X lines
    for x in range(0,LAND_NUM_X):
        pygame.draw.line(ScreenSurface, RED, (x*LAND_CELL_WIDTH, 0),\
                        (x*LAND_CELL_WIDTH, WINDOW_HEIGHT-1))

    #drawing maximum Y line
    pygame.draw.line(ScreenSurface, RED, (0, WINDOW_HEIGHT-1),\
                    (FIELD_WIDTH, WINDOW_HEIGHT-1))

    #drawing maximum X line
    pygame.draw.line(ScreenSurface, RED, (FIELD_WIDTH, 0),\
                    (FIELD_WIDTH, WINDOW_HEIGHT-1))

    #Draw panel
    pygame.draw.line(ScreenSurface, GREEN, (WINDOW_WIDTH-SIDE_PANEL_WIDTH, 0),\
                    (WINDOW_WIDTH - 1, 0))
    pygame.draw.line(ScreenSurface, GREEN, (WINDOW_WIDTH-SIDE_PANEL_WIDTH, 0),\
                    (WINDOW_WIDTH-SIDE_PANEL_WIDTH, WINDOW_HEIGHT-1))
    pygame.draw.line(ScreenSurface, GREEN, (WINDOW_WIDTH - 1, 0),\
                    (WINDOW_WIDTH - 1, WINDOW_HEIGHT-1))
    pygame.draw.line(ScreenSurface, GREEN, (WINDOW_WIDTH-SIDE_PANEL_WIDTH, WINDOW_HEIGHT-1),\
                    (WINDOW_WIDTH - 1, WINDOW_HEIGHT-1))
        
    return True

def cellToPxCoordinate(cell_coordinates):
    px_coordinates = (cell_coordinates[0] * LAND_CELL_WIDTH+LAND_CELL_WIDTH // 2,
                      cell_coordinates[1] * LAND_CELL_WIDTH+LAND_CELL_HEIGHT // 2)
    return px_coordinates

def pxToCellCoordinate(coordinates):
    px_coordinates = ((coordinates[0] - coordinates[0] % LAND_CELL_WIDTH) // LAND_CELL_WIDTH,
                      (coordinates[1] - coordinates[1] % LAND_CELL_WIDTH) // LAND_CELL_WIDTH)
    return px_coordinates













if __name__ == '__main__':
    main() 
