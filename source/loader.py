import glob
import pygame
from source import tools

#CONSTANTS
#Uplading constants from setup.ini file
from source import tools

constants = tools.importConstants()
'''___________________________________________________________'''
#Game directories
LAND_TILES_DIR  = constants['LAND_TILES_DIR']   #Default is 'tiles\\'
SPRITES_DIR     = constants['SPRITES_DIR']      #Default is 'sprite\\'
CONTROLS_DIR    = constants['CONTROLS_DIR']     #Default is 'controls\\'
MARKERS_DIR     = constants['MARKERS_DIR']      #Default is 'markers\\'
ICONS_DIR       = constants['ICONS_DIR']        #Default is 'icons\\'
BACKGROUNDS_DIR = constants['BACKGROUNDS_DIR']  #Default is 'backgrounds\\'
POPUPS_DIR      = constants['POPUPS_DIR']       #Default is 'popups\\'
#Loader image categories
SPRITE      = constants['SPRITE']       #Default is 'sprite'
TILE        = constants['TILE']         #Default is 'tile'
CONTROLS    = constants['CONTROLS']     #Default is 'controls'
MARKER      = constants['MARKER']       #Default is 'marker'
ICON        = constants['ICON']         #Default is 'icon'
BUTTON      = constants['BUTTON']       #Default is 'button'
POPUP       = constants['POPUP']        #Default is 'popup'
BACKGROUND  = constants['BACKGROUND']   #Default is 'background'
#Cell width and height
LAND_CELL_HEIGHT= constants['LAND_CELL_HEIGHT'] #Calculated
LAND_CELL_WIDTH = LAND_CELL_HEIGHT
#Debug
LOADER_DEBUG    = constants['LOADER_DEBUG']
del constants

BUTTON_SIZE = 35
'''___________________________________________________________'''

class Loader:
    """ Helper class for uploading main and custom character sprites
    and land textures"""
    
    def __init__(self):
        '''
        (None)-> NoneType

        Building databese(via two dictionaries) for basic sprites and
        tiles that located in corresponding root folders.

        For player and enemies, slises sprites them on frames(50x50px)
        '''

        #Defining dictionary databases
        self.sprites = {}
        self.tiles = {}
        self.controls = {}
        self.cash = {
            SPRITE:{},
            TILE:{},
            BACKGROUND:{},
            CONTROLS:{},
            ICON:{},
            BUTTON:{},
            POPUP:{},
            MARKER:{}
        }
        self.get('controls','error')

        return None

    def _sprite_sliser(self, path):
        '''
        (str) -> list of lists

        Loading animation from strips file where all frames 50x50px.
        Movement direction by indexes:
        -------
        |7|8|9|
        -------
        |4|_|6|
        -------
        |1|2|3|
        -------
        Values for 0 and 5 direction are NoneType as not valid.
        '''
        SIZE = 50
        strip_image = pygame.image.load(path).convert()

        direct_sprites = []
        mirrored_sprites = []
        
        for d in range(5):
            one_way = []
            mirrored_way = []
            for i in range(5):
                tmp_img = strip_image.subsurface(SIZE*d, SIZE*i, SIZE, SIZE)
                tmp_img = pygame.transform.scale(tmp_img, (SIZE, SIZE))
                one_way.append(tmp_img)
                mirrored_way.append(pygame.transform.flip(tmp_img, True, False))
            direct_sprites.append(one_way)
            #print(len(one_way))
            mirrored_sprites.append(mirrored_way)

        result = (None,\
                  direct_sprites[0], direct_sprites[1], mirrored_sprites[0],\
                  direct_sprites[2], None,              mirrored_sprites[2],\
                  direct_sprites[3], direct_sprites[4], mirrored_sprites[3])
        
        return result

    def get(self, table, img_name):
        '''
        (str, str) -> Surface

        Returns image surface from corresponding image dictionary
        '''
        assert table in self.cash, 'Incorrect category request passed to Loader'
        if img_name in self.cash[table]:
            return self.cash[table][img_name]
        else:
            exists = self._load_content(table,img_name)
            if exists:
                return self.cash[table][img_name]
            else:
                return self.cash['controls']['error']

    def _load_content(self, table,img_name):
        '''
        (str, str) -> bool

        Calls method responsible for certain image type downloading.
        Return True if image exists and successfully loaded, otherwise
        returns False.
        '''
        def _icon(img_name, button = False):
            '''
            (str) -> bool

            If image exists in 'icons' directory - loads it and returns True.
            Otherwise returns False.
            Loaded image is added to 'icon' dictionary with white as
            transparency color key or to 'buttons' dictionary with black one.
            '''
            if button:
                color_key = (0,0,0,255)
            else:
                color_key = (255,255,255,255)
            path = ICONS_DIR
            if tools.file_exists(path, img_name + '.png'):
                filename = path + img_name + '.png'
                processed_image = pygame.image.load(filename).convert()
                processed_image = pygame.transform.scale(processed_image,\
                                       (BUTTON_SIZE, BUTTON_SIZE))
                processed_image.set_colorkey(color_key)
                if button:
                    self.cash[BUTTON][img_name] = processed_image
                else:
                    self.cash[ICON][img_name] = processed_image
                if LOADER_DEBUG:
                    if button:
                        dest = BUTTON
                    else:
                        dest = ICON
                    print('LOADER', filename, 'loaded to', dest)
                return True
            else:
                return False

        def _tile(img_name):
            '''
            (str) -> bool

            If tile image exists in 'tile' directory - loads it and
            returns True. Otherwise returns False.
            '''
            if tools.file_exists(LAND_TILES_DIR, img_name + '.png'):
                filename = LAND_TILES_DIR + img_name + '.png'
                processed_image = pygame.image.load(filename).convert()
                processed_image = pygame.transform.scale(processed_image,\
                                       (LAND_CELL_WIDTH, LAND_CELL_HEIGHT))
                self.cash[TILE][img_name] = processed_image
                if LOADER_DEBUG:
                    print('LOADER', filename, 'loaded to tiles')
                return True
            else:
                return False

        def _image(img_name, location):
            '''
            (str) -> bool

            If image exists in LOCATION directory - loads it and
            returns True. Otherwise returns False. No scaling is applied
            '''
            if location == BACKGROUND:
                directory = BACKGROUNDS_DIR
            elif location == POPUP:
                directory = POPUPS_DIR

            if tools.file_exists(directory, img_name + '.png'):
                filename = directory + img_name + '.png'
                processed_image = pygame.image.load(filename).convert()
                self.cash[location][img_name] = processed_image
                if LOADER_DEBUG:
                    print('LOADER', filename, 'loaded to',location)
                return True
            else:
                return False

        def _sprite(sprite):
            '''
            (str) -> bool

            If sprite image exists in 'sprites' directory - loads it and
            returns True. Otherwise returns False. No scaling is applied
            '''
            if tools.file_exists(SPRITES_DIR, sprite + '.png'):
                filename = SPRITES_DIR + sprite + '.png'
                sprite_list = self._sprite_sliser(filename)
                self.cash[SPRITE][img_name] = sprite_list
                if LOADER_DEBUG:
                    print('LOADER', filename, 'loaded to sprites')
                return True
            else:
                return False

        def _controls(img_name):
            '''
            (str) -> bool

            If image exists in 'controls' directory or its 'icons' or
            'buttons' sub folders - loads it and returns True.
            Otherwise returns False.
            '''
            if tools.file_exists(CONTROLS_DIR, img_name + '.png'):
                filename = CONTROLS_DIR + img_name + '.png'
                processed_image = pygame.image.load(filename).convert()
                self.cash[CONTROLS][img_name] = processed_image
                if LOADER_DEBUG:
                    print('LOADER', filename, 'loaded to controls')
                return True
            else:
                return False

        def _marker(img_name):
            '''
            (str) -> bool

            If marker exists in 'marker' directory - loads it and
            returns True. Otherwise returns False.
            '''
            if tools.file_exists(MARKERS_DIR, img_name + '.png'):
                filename = MARKERS_DIR + img_name + '.png'
                processed_image = pygame.image.load(filename).convert()
                self.cash[MARKER][img_name] = pygame.transform.\
                    scale(processed_image,(LAND_CELL_WIDTH, LAND_CELL_HEIGHT))
                if LOADER_DEBUG:
                    print('LOADER', filename, 'loaded to markers')
                return True
            else:
                return False

        if table == ICON:
            return _icon(img_name)
        elif table == BUTTON:
            return _icon(img_name, button=True)
        elif table == POPUP:
            return _image(img_name,POPUP)
        elif table == TILE:
            return _tile(img_name)
        elif table == BACKGROUND:
            return _image(img_name,BACKGROUND)
        elif table == MARKER:
            return _marker(img_name)
        elif table == SPRITE:
            return _sprite(img_name)
        elif table == CONTROLS:
            return _controls(img_name)

















