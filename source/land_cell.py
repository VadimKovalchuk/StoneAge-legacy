import pygame

#CONSTANTS
#Uplading constants from setup.ini file
from source import tools
constants = tools.Constants()
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
#Resource richness in land cell
EMPTY = constants['EMPTY']      #Default is 'empty'
LOW = constants['LOW']          #Default is 'low'
MODERATE = constants['MODERATE']#Default is 'moderate'
MANY = constants['MANY']        #Default is 'many'
RICH = constants['RICH']        #Default is 'rich'
del constants

MARKER_PRIORITY = ['activity','selection']
'''___________________________________________________________'''

class LandCell:
    """ Land cell class """

    def __init__(self, cell_index, land_type, preset, cell_coords, Loader):
        '''
        (land_cell, str, int, (int, int)) -> NoneType

        Contains all information about lend cell:
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
        self.tile_img = self.Loader.get('tile',land_type)
        self.resources = {'food':0, 'hunt':0, 'wood':0, 'stone':0}
        self.resource_limit = {}
        self.predators = {'bear':0, 'wolfs':0, 'boar':0,'snake':0,
                          'rockfall':0, 'drawn':0}
        self.markers = []
        self.custom= {}

        #Preset processing
        self._init_preset(preset)
        
        return None

    def blit(self, Surface):
        '''
        (Surface) -> True

        Blits land tile on map Surface.
        '''
        Surface.blit(self.tile_img, self.rect)

        return True

    def blit_markers(self, Surface):
        '''
        (Surface) -> None

        Blits marker over the map and sprites.
        '''
        for marker in MARKER_PRIORITY:
            if marker in self.markers:
                Surface.blit(self.Loader.get('marker', marker), self.rect)

        return None
                        
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
                self.resources['food'] = 100
                self.resources['hunt'] = 200
            elif self.land_type == FOREST:
                self.resources['food'] = 300
                self.resources['hunt'] = 500
                self.resources['wood'] = 500
            elif self.land_type == MOUNTAIN:
                self.resources['food'] = 50
                self.resources['hunt'] = 100
                self.resources['stone'] = 500
            elif self.land_type == WATER:
                self.resources['hunt'] = 500
        elif preset in ('player','CPU'):
            self.custom['preset'] = preset

        self.resource_limit = self.resources.copy()

        return None

    def regenerate(self, resource = None, amount = None):
        '''
        (None) -> None

        Regenerates specified resource(in case of custom event) or all
        resources on daily basis.
        '''
        if resource:
            pass
        else:
            if self.land_type == FIELD:
                res_list = ('food', 'hunt')
            elif self.land_type == FOREST:
                res_list = ('food', 'hunt', 'wood')
            elif self.land_type == MOUNTAIN:
                res_list = ('food', 'hunt', 'stone')
            elif self.land_type == WATER:
                res_list = ('hunt',)
            else:
                return None
            for resource in res_list:
                if self.resources[resource] == self.resource_limit[resource]:
                    continue
                else:
                    self.resources[resource] += 1

        return None

    def richness(self,resource):
        '''
        (str) -> str

        Calculates and returns richness of passed resource type
        '''
        if self.resources[resource] <= 0:
            self.resources[resource] = 0
            return EMPTY
        margin = self.resources[resource]/self.resource_limit[resource]
        if margin > 0.8:
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

        return self.resources[resource]

    def decrease_resource(self,resource, amount):
        '''
        (str, int) -> None

        Decreases specified resource amount
        '''
        self.resources[resource] -= amount

        return None










