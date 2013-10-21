import pygame

#CONSTANTS
#Uplading constants from setup.ini file
from source import tools

constants = {}
constants = tools.importConstants()
'''___________________________________________________________'''
#Cell width and height
LAND_CELL_HEIGHT= constants['LAND_CELL_HEIGHT'] #Calculated
LAND_CELL_WIDTH = LAND_CELL_HEIGHT
#Movement dirrection constants
DOWN_LEFT       = constants['DOWN_LEFT']        #Default 1
LEFT_DOWN       = DOWN_LEFT
DOWN            = constants['DOWN']             #Default 2
DOWN_RIGHT      = constants['DOWN_RIGHT']       #Default 3
RIGHT_DOWN      = DOWN_RIGHT
LEFT            = constants['LEFT']             #Default 4
RIGHT           = constants['RIGHT']            #Default 6
UP_LEFT         = constants['UP_LEFT']          #Default 7
LEFT_UP         = UP_LEFT
UP              = constants['UP']               #Default 8
UP_RIGHT        = constants['UP_RIGHT']         #Default 9
RIGHT_UP        = UP_RIGHT
del constants
'''___________________________________________________________'''

class Tribesman:
    """ Single man from tribe class """

    def __init__(self, Sprite, name, cell_coords, instrument = None, wear = None, custom = None):
        '''
        (Sprite, str, (int, int), str, str, dict) -> NoneType

        Contains all information about tribesman:
        - name
        - land cell coordinates (x, y);
        - absolute coordinates
        - (!not implemented) tribesman rectangle
        - owned instrument/weapon;
        - weared costume/armor;
        - inventory (dictionary where key is a item and value is its nuber)
        - custom atribute for quests purposes
        '''
        
        self.Sprite = Sprite #actual sprite
        self.cell = cell_coords #Location cell coordinates(X,Y) on map
        self.visible = False # visible or invisible character
        self.Rect = pygame.Rect((0,0), (50, 50))
        self.setLocation(self.cell)

        self.name = name #tribesman name
        self.points = 5
        self.instrument = instrument #available instrument/weapon
        self.wear = wear # weared costume/armor
        self.inventory = [] # caryed resources and items
        self.custom = custom

        ''' FRAME TRACKING VARIABLES
        Track the time we started, and the time between updates.
        Then we can figure out when we have to switch the image.
        '''
        #self.f_start = pygame.time.get_ticks()
        self.frame_delay = 100
        self.frame_last_update = 0
        self.frame = 0
        # Call update_frame_index to set our first image.
        self._updateFrameIndex()

        ''' MOVEMENT TRACKING VARIABLES '''
        self.m_speed = 1
        self.m_destination_cell = None
        self.m_cell_difference = ()
        self.m_waypoints = []
        self.m_movement_direction = DOWN_LEFT
        
        return None

    def _updateFrameIndex(self):
        # Note that this doesn't work if it's been more that self._delay
        # time between calls to update(); we only update the image once
        # then, but it really should be updated twice.
        time = pygame.time.get_ticks()
        if time - self.frame_last_update > self.frame_delay:
            self.frame += 1
            if self.frame >= 5: self.frame = 0
            self.frame_last_update = time

        return None
                        
    def __str__(self):
        '''
        (land_cell) -> str

        Return clases content.

        >>> cell = land_cell(1, 180, (1,1))
        >>> print(cell)
        
        '''
        return str(self.name)+" is at x="+str(self.cell[0])+", y="\
               +str(self.cell[1])

    def blit(self, ScreenSurface):
        '''
        (Surface) -> NoneType
        
        Draw tribesman actual sprite frame
        in map coordinates defined by its rect
        '''
        
        if self.visible == True:
            if self.m_movement_direction not in [1,2,3,4,6,7,8,9]:
                self.m_movement_direction = 3
            ScreenSurface.blit(self.Sprite[self.m_movement_direction]\
                               [self.frame], self.Rect)

        return None

    def setLocation(self, cell_coordinates):
        '''
        (tuple of ints) -> NoneType

        Tuple should contain 2 ints.
        Teleports tribesman to specifyed cell location.
        '''
        
        self.cell = cell_coordinates
        self.Rect.center = tools.cellToPxCoordinate(self.cell)

        return None
    
    def travel(self, waypoints):
        '''
        (list of tuples of ints) -> NoneType

        Prepearing and initializing tribesman heading to specifyed location
        by passed waypoints coordinates.
        '''
        # Becomes visible while traveling
        self.visible = True 
        self.m_waypoints = waypoints[:]

        # Gets first waypoint from waypoints
        self.m_destination_cell = self.m_waypoints[0] 
        del self.m_waypoints[0] 

        # Gets difference between heading coordinate and current for using
        # in selection for movement and corresponding way sprite 
        self.m_cell_difference = (self.m_destination_cell[0] - self.cell[0],\
                                  self.m_destination_cell[1] - self.cell[1])
        # Movement way calculation
        self.m_movement_direction = 5 + self.m_cell_difference[0]\
                                    - self.m_cell_difference[1] * 3

        return None

    def move(self):
        '''
        (NoneType) -> NoneType

        Method that perform traveling process from cell to cell and updates
        animation
        '''
        
        if self.visible == False:
            return None

        #Updating frame index
        self._updateFrameIndex()
        
        # If tribesman reached waypoint than processing path to next waypoint
        if self.Rect.center == tools.cellToPxCoordinate(self.m_destination_cell):

            # Destination cell becones location cell
            self.cell = self.m_destination_cell

            # Tacking next waypoint as destination
            if len(self.m_waypoints) > 0:
                self.m_destination_cell = self.m_waypoints[0]
                self.m_waypoints.pop(0)
            else:
                #If no waypoints are left it means that destination is reached
                self.visible = False
                return None

            # Updating tribesman rectangle in case if any error in coordinates
            # calculation occurs
            self.Rect.center = tools.cellToPxCoordinate(self.cell)

            # Gets difference between heading coordinate and current for using
            # in selection for movement and corresponding way sprite
            self.m_cell_difference = (self.m_destination_cell[0] - self.cell[0],\
                                      self.m_destination_cell[1] - self.cell[1])

            # Movement way calculation
            self.m_movement_direction = 5 + self.m_cell_difference[0] -\
                                        self.m_cell_difference[1] * 3

        #Move tribesman rectangle
        self.Rect.move_ip(self.m_cell_difference[0]*self.m_speed,\
                          self.m_cell_difference[1]*self.m_speed)

        return None
        
        
        



        
