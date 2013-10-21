import glob

import pygame

#CONSTANTS
#Uplading constants from setup.ini file
from source import tools

constants = {}
constants = tools.importConstants()
'''___________________________________________________________'''
#Game directories
LAND_TILES_DIR  = constants['LAND_TILES_DIR']   #Default is 'tiles\\'
SPRITES_DIR     = constants['SPRITES_DIR']      #Default is 'sprite\\'
CONTROLS_DIR     = constants['CONTROLS_DIR']    #Default is 'controls\\'
#Cell width and height
LAND_CELL_HEIGHT= constants['LAND_CELL_HEIGHT'] #Calculated
LAND_CELL_WIDTH = LAND_CELL_HEIGHT
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

        #Building sprite database
        files = self._build_load_list(SPRITES_DIR)
        for file in files:
            base_name = file[:-4]
            self.sprites[base_name] = self._sprite_sliser(SPRITES_DIR\
                                                          + file)

        #Building tiles database
        files = self._build_load_list(LAND_TILES_DIR)

        for file in files:
            procesed_image = pygame.image.load(LAND_TILES_DIR + file)\
                             .convert()
            base_name = file[:-4]
            self.tiles[base_name] = pygame.transform.scale(procesed_image,\
                                       (LAND_CELL_WIDTH, LAND_CELL_HEIGHT))

        #Building control elements images database
        files = self._build_load_list(CONTROLS_DIR)
        for file in files:
            procesed_image = pygame.image.load(CONTROLS_DIR + file)
            procesed_image = procesed_image.convert()

            if 'icon' in file:
                procesed_image = pygame.transform.scale(procesed_image,\
                                       (BUTTON_SIZE, BUTTON_SIZE))
                base_name = file[:-8] + 'button'
                procesed_image.set_colorkey((0,0,0,255))
                self.controls[base_name] = procesed_image.copy()

            if 'button' in file:
                procesed_image = pygame.transform.scale(procesed_image,\
                                       (BUTTON_SIZE, BUTTON_SIZE))

            procesed_image.set_colorkey((255,255,255,255))
            base_name = file[:-4]
            self.controls[base_name] = procesed_image

        print("Sprite files:")
        self.print_table(self.sprites)
        print('\n',"Land texture files:")
        self.print_table(self.tiles)
        print('\n',"Images for control system:")
        self.print_table(self.controls)

        return None

    def _build_load_list(self, path):
        '''
        (str) -> list

        Gets directory path and returns list of files with .png extention
        '''

        files = glob.glob(path + "*.png")
        
        for file in files[:]:
            files.remove(file)
            files.append(file[len(path):])
        
        return files

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

    def print_table(self, output_dict):
        '''
        (list) -> None

        Prints(on screen so far) list of dictionary's keys with 4 elements in row
        '''
        result_str = ''
        counter = 0
        for key in output_dict:
            result_str += str(key) + ',\t'
            counter += 1
            if counter % 4 == 0:
                result_str += '\n'
        print(result_str)

        return None

