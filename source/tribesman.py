import pygame

#CONSTANTS
#Uplading constants from setup.ini file
from source import tools

constants = {}
constants = tools.Constants()
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

    def __init__(self, Sprite, name, cell_coords):
        '''
        (Sprite, str, (int, int), str, str, dict) -> NoneType

        Contains all information about tribesman:
        - name
        - land cell coordinates (x, y);
        - absolute coordinates
        - (!not implemented) tribesman rectangle
        - owned instrument/weapon;
        - worn costume/armor;
        - inventory (dictionary where key is a item and value is its nuber)
        - custom attribute for quests purposes
        '''
        
        self.Sprite = Sprite #actual sprite
        self.cell = cell_coords #Location cell coordinates(X,Y) on map
        self.visible = False # visible or invisible character
        self.rect = pygame.Rect((0,0), (50, 50))
        self.setLocation(self.cell)

        self.name = name #tribesman name
        self.points = 5
        self.weapon = None
        self.wear = None
        self.inventory = [None, None, None] # carried resources and items



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

    def suffer(self,damage = 1):
        '''
        (int) -> bool

        Deals damage to tribesman. If damage is higher than current health
        than set to 0 (it means that tribesman should die).
        '''
        if self.points > damage:
            self.points -= damage
        else:
            self.points = 0

        return None

    def heal(self,amount = 1):
        '''
        (int) -> bool

        Heals tribesman with passed points amount but not higher
        than limit in 5 points.
        '''
        if self.points + amount >= 5:
            self.points = 5
        else:
            self.points += amount

        return None

    def is_alive(self):
        '''
        (None) -> bool

        Verifies is tribesman is dead.
        True - alive
        False- dead
        '''
        if self.points == 0:
            return False
        elif self.points > 0:
            assert 0 <= self.points <= 5, \
                'Incorrect number of health points'
            return True

    def add_item(self,item):
        '''
        (list) -> None

        Adds item into tribesman inventory. If this is a weapon or armor
        and tribesman already equipped with this item type - returns old one.
        '''
        item.owner = self
        if item.type in ('weapon', 'range'):
            if not self.weapon:
                self.weapon = item
                return None
            else:
                returned, self.weapon = self.weapon, item
                returned.owner = None
                return returned
        elif item.type == 'armor':
            if not self.wear:
                self.wear = item
                return None
            else:
                returned, self.wear = self.wear, item
                returned.owner = None
                return returned
        else:
            self.inventory.append(item)
        return None

    def hit(self):
        '''
        (None) -> int

        Deals hit points according to equipped weapon. If no weapon is equipped
        deals 1 hit point.
        '''
        if self.weapon:
            if self.weapon.consumable:
                found = False
                for item in self.inventory:
                    if item:
                        for consumable_id in self.weapon.consumable:
                            if consumable_id == item.id:
                                item.amount -= 1
                                if item.amount == 0:
                                    self.inventory.remove(item)
                                    self.inventory.append(None)
                                points = self.weapon.hit(consumable_id)
                                found = True
                                break
                    if found:
                        break
                else:
                    points = 1
            else:
                points = self.weapon.hit()
            if self.weapon.expired_durability():
                self.weapon = None
        else:
            points = 1
        return points

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
                               [self.frame], self.rect)

        return None

    def setLocation(self, cell_coordinates):
        '''
        (tuple of ints) -> NoneType

        Tuple should contain 2 ints.
        Teleports tribesman to specifyed cell location.
        '''
        
        self.cell = cell_coordinates
        self.rect.center = tools.cellToPxCoordinate(self.cell)

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
        if self.rect.center == tools.cellToPxCoordinate(self.m_destination_cell):

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
            self.rect.center = tools.cellToPxCoordinate(self.cell)

            # Gets difference between heading coordinate and current for using
            # in selection for movement and corresponding way sprite
            self.m_cell_difference = (self.m_destination_cell[0] - self.cell[0],\
                                      self.m_destination_cell[1] - self.cell[1])

            # Movement way calculation
            self.m_movement_direction = 5 + self.m_cell_difference[0] -\
                                        self.m_cell_difference[1] * 3

        #Move tribesman rectangle
        self.rect.move_ip(self.m_cell_difference[0]*self.m_speed,\
                          self.m_cell_difference[1]*self.m_speed)

        return None
        
    def __str__(self):
        '''
        (land_cell) -> str

        Return clases content.

        >>> cell = land_cell(1, 180, (1,1))
        >>> print(cell)

        '''
        string = str(self.name)+"("+str(self.points)+"points)"
        if self.weapon:
            string += ',WP:' + str(self.weapon)
        if self.wear:
            string += ',WR:' + str(self.wear)
        for item in self.inventory:
            string += ',' + str(self.wear)
        string += '. '
        return string

        



        
