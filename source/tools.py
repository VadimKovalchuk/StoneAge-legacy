import glob

#Set up window resolution
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
#Number of cells by X and Y axises
LAND_NUM_Y = 4
LAND_NUM_X = 6
#Side(control) panel and game field width
SIDE_PANEL_WIDTH = WINDOW_WIDTH - WINDOW_HEIGHT // LAND_NUM_Y * LAND_NUM_X
FIELD_WIDTH = WINDOW_WIDTH - SIDE_PANEL_WIDTH
#Cell width and height
LAND_CELL_HEIGHT = WINDOW_HEIGHT // LAND_NUM_Y
LAND_CELL_WIDTH = LAND_CELL_HEIGHT

def main():
    constants = {}
    output_list= []
    
    constants['LANGUAGE']           = str('EN')
    constants['WINDOW_WIDTH']       = str(WINDOW_WIDTH)
    constants['WINDOW_HEIGHT']      = str(WINDOW_HEIGHT)
    constants['FPS']                = str(40)
    constants['BROWN']              = str((165, 42, 42))
    constants['ORANGE']             = str((255, 165, 0))
    constants['LAND_TILES_DIR']     = str('tiles\\')
    constants['SPRITES_DIR']        = str('sprite\\')
    constants['SCENARIO_DIR']       = str('scenario\\')
    constants['CONTROLS_DIR']       = str('controls\\')
    constants['MARKERS_DIR']        = str('markers\\')
    constants['ICONS_DIR']          = str('icons\\')
    constants['BACKGROUNDS_DIR']    = str('backgrounds\\')
    constants['POPUPS_DIR']         = str('popups\\')
    constants['TXT_SUBFOLDER']      = str('text\\')
    constants['TILE']               = str('tile')
    constants['SPRITE']             = str('sprite')
    constants['CONTROLS']           = str('controls')
    constants['MARKER']             = str('marker')
    constants['ICON']               = str('icon')
    constants['BACKGROUND']         = str('background')
    constants['POPUP']              = str('popup')
    constants['BUTTON']             = str('button')
    constants['LAND_NUM_Y']         = str(LAND_NUM_Y)
    constants['LAND_NUM_X']         = str(LAND_NUM_X)
    constants['SEND_INTERVAL']      = str(700)
    constants['FIELD']              = str('field')
    constants['FOREST']             = str('forest')
    constants['MOUNTAIN']           = str('mountain')
    constants['WATER']              = str('water')
    constants['CAMP']               = str('camp')
    constants['SIDE_PANEL_WIDTH']   = str(SIDE_PANEL_WIDTH)
    constants['FIELD_WIDTH']        = str(FIELD_WIDTH)
    constants['LAND_CELL_HEIGHT']   = str(LAND_CELL_HEIGHT)
    constants['DOWN_LEFT']          = str(1)
    constants['DOWN']               = str(2)
    constants['DOWN_RIGHT']         = str(3)
    constants['LEFT']               = str(4)
    constants['RIGHT']              = str(6)
    constants['UP_LEFT']            = str(7)
    constants['UP']                 = str(8)
    constants['UP_RIGHT']           = str(9)
    constants['EMPTY']              = str('empty')
    constants['LOW']                = str('low')
    constants['MODERATE']           = str('moderate')
    constants['MANY']               = str('many')
    constants['RICH']               = str('rich')
    constants['FOOD']               = str('food')
    constants['STOCKED_FOOD']       = str('stocked_food')
    constants['HIDDEN_BONES']       = str('hidden_bones')
    constants['BONES']              = str('bones')
    constants['MOIST_SKIN']         = str('moist_skin')
    constants['SKIN']               = str('skin')
    constants['WOOD']               = str('wood')
    constants['STONE']              = str('stone')
    constants['PATHFINDER_DEBUG']   = str('')
    constants['LOADER_DEBUG']       = str('')

    output_list.append('\nActive language')
    output_list.append('LANGUAGE')
    output_list.append('\nSet up window resolution')
    output_list.append('WINDOW_WIDTH')
    output_list.append('WINDOW_HEIGHT')
    output_list.append('FPS')
    output_list.append('\nColors')
    output_list.append('BROWN')
    output_list.append('ORANGE')
    output_list.append('\nGame directories')
    output_list.append('LAND_TILES_DIR')
    output_list.append('SPRITES_DIR')
    output_list.append('SCENARIO_DIR')
    output_list.append('CONTROLS_DIR')
    output_list.append('MARKERS_DIR')
    output_list.append('ICONS_DIR')
    output_list.append('BACKGROUNDS_DIR')
    output_list.append('POPUPS_DIR')
    output_list.append('TXT_SUBFOLDER')
    output_list.append('\nLoader image categories')
    output_list.append('TILE')
    output_list.append('SPRITE')
    output_list.append('CONTROLS')
    output_list.append('MARKER')
    output_list.append('ICON')
    output_list.append('BACKGROUND')
    output_list.append('POPUP')
    output_list.append('BUTTON')
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
    output_list.append('\nDebug')
    output_list.append('PATHFINDER_DEBUG')
    output_list.append('LOADER_DEBUG')

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

def cellToPxCoordinate(cell_coordinates):
    px_coordinates = (cell_coordinates[0] * LAND_CELL_WIDTH+LAND_CELL_WIDTH // 2,
                      cell_coordinates[1] * LAND_CELL_WIDTH+LAND_CELL_HEIGHT // 2)
    return px_coordinates

def pxToCellCoordinate(coordinates):
    px_coordinates = ((coordinates[0] - coordinates[0] % LAND_CELL_WIDTH) // LAND_CELL_WIDTH,
                      (coordinates[1] - coordinates[1] % LAND_CELL_WIDTH) // LAND_CELL_WIDTH)
    return px_coordinates

def file_exists(path ,filename):
    '''
    (str,str) -> bool

    Return True if file exists in following directory
    '''
    files = glob.glob(path + '*')
    for file in files[:]:
        files.remove(file)
        files.append(file[len(path):])

    return filename in files













if __name__ == '__main__':
    main() 
