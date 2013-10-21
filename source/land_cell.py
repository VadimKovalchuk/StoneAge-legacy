import pygame

#CONSTANTS
#Uplading constants from setup.ini file
from source import tools
constants = tools.importConstants()
'''___________________________________________________________'''
#Cell width and height
LAND_CELL_HEIGHT= constants['LAND_CELL_HEIGHT'] #Calculated
LAND_CELL_WIDTH = LAND_CELL_HEIGHT
#Land cell types
FIELD = constants['FIELD']      #Default is 'field'
FOREST = constants['FOREST']    #Default is 'forest'
MOUNTAIN = constants['MOUNTAIN']#Default is 'mountain'
WATER = constants['WATER']      #Default is 'water'
CAMP = constants['CAMP']        #Default is 'camp'
EMPTY = constants['EMPTY']      #Default is 'empty'
LOW = constants['LOW']          #Default is 'low'
MODERATE = constants['MODERATE']#Default is 'moderate'
MANY = constants['MANY']        #Default is 'many'
RICH = constants['RICH']        #Default is 'rich'
del constants
'''___________________________________________________________'''

class LandCell:
    """ Land cell class """

    def __init__(self, cell_index, land_type, preset, cell_coords, Loader):
        '''
        (land_cell, str, int, (int, int)) -> NoneType

        Contains all infirmation about lend cell:
        - absolute land index
        - land type(grass, forest, water, rock, custom)
        - Reference to Loader object
        - cell coordinates (x, y)
        - cell rectangle
        - (!not implemented) resource capasity 
        - (!not implemented) predators (dictionary where key is a predator
           and value - atack chance)
        
        '''
        self.index = cell_index
        self.land_type = land_type
        self.cell = cell_coords
        self.rect = pygame.Rect(self.cell[0]*LAND_CELL_WIDTH,\
                                self.cell[1]*LAND_CELL_HEIGHT,\
                                LAND_CELL_WIDTH, LAND_CELL_HEIGHT)
        self.Loader = Loader
        self.tile_img = self.Loader.tiles[land_type]
        self.resourses = {'food':0, 'hunt':0, 'wood':0, 'stone':0}
        self.resource_limit = {}
        self.predators = {'bear':0, 'wolfs':0, 'boar':0,'snake':0,
                          'rockfall':0, 'drawn':0}
        self.custom= {}

        #Preset processing
        self._init_preset(preset)
        
        return None

    def blit(self, Surface):
        '''
        (Surface) -> True
        '''
        Surface.blit(self.tile_img, self.rect)
        

        return True
                        
    def __str__(self):
        '''
        (land_cell) -> str

        Return type and coordinates in string context.
        '''
        return "\n land_type="+str(self.land_type)+", x="+str(self.cell[0])\
               +", y="+str(self.cell[1]) 

    def _init_preset(self,preset):

        if preset == 'default':
            if self.land_type == FIELD:
                self.resourses['food'] = 100
                self.resourses['hunt'] = 200
            elif self.land_type == FOREST:
                self.resourses['food'] = 300
                self.resourses['hunt'] = 500
                self.resourses['wood'] = 500
            elif self.land_type == MOUNTAIN:
                self.resourses['food'] = 50
                self.resourses['hunt'] = 100
                self.resourses['stone'] = 500
            elif self.land_type == WATER:
                self.resourses['hunt'] = 500
        elif preset in ('player','CPU'):
            self.custom['preset'] = preset

        self.resource_limit = self.resourses.copy()

        return None

    def richness(self,resource):
        '''
        (str) -> str

        Calculates and returns richness of passed resource type
        '''
        if self.resourses[resource] == 0:
            return EMPTY
        margin = self.resource_limit[resource]/self.resourses[resource]
        if 1 >= margin > 0.8:
            return RICH
        elif 0.8 >= margin > 0.5:
            return MANY
        elif 0.5 >= margin > 0.2:
            return MODERATE
        elif 0.2 >= margin > 0:
            return LOW

    def get_resource(self,resource):
        '''
        (str) -> int

        Returns passed type of resource
        '''

        return self.resourses[resource]











