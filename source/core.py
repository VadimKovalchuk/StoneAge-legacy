from source import tools, land_cell, tribe
from source import path_finder
from source import rules

#CONSTANTS
#Uplading constants from setup.ini file

constants = tools.importConstants()
'''___________________________________________________________'''
#Number of cells by X and Y axises
LAND_NUM_Y      = constants['LAND_NUM_Y']       #Default 4
LAND_NUM_X      = constants['LAND_NUM_X']       #Default 6
del constants
#Game phases
MORNING = 0
SEND = 1
DAY = 2
RETURN = 3
EVENING = 4
'''___________________________________________________________'''

class Core:
    """ Map class contains game logic with landscape structure, tribe
    location, movement and interaction of lend cells and tribesmen inside
    the parties """

    def __init__(self,ScreenSurface, Scenario, Loader):
        '''
        (Surface, Scenarion) -> NoneType

        Loads map via scenario and builds it with land cells
        '''

        self.ScreenSurface = ScreenSurface
        self.ClearLandscape = ScreenSurface.copy()
        self.Scenario = Scenario
        self.Loader = Loader
        self.map = []
        self.active_sprites = []
        self.tribes = []
        self.active_tribe = None
        self.PathFinder = None
        self.Rules = rules.Rules(self)
        self.game_mode = 'regular'
        self.game_phase = 0
        self.move_counter = 0
        self.update = False
        self.popup = None

        # Building starting map from map line
        for x in range(0,LAND_NUM_X):
            y_line = []
            for y in range(0,LAND_NUM_Y):
                cell_ref = land_cell.LandCell(
                                    self.Scenario.map_line[x][y]['cell_index'],
                                    self.Scenario.map_line[x][y]['land_type'],
                                    self.Scenario.map_line[x][y]['preset'],
                                    (x,y),
                                    self.Loader)
                y_line.append(cell_ref)
            self.map.append(y_line)

        # Creating tribes
        for x in range(0,LAND_NUM_X):
            for y in range(0,LAND_NUM_Y):
                if self.map[x][y].land_type == 'camp':
                    tribe_ref = tribe.Tribe(str(x)+str(y),Loader,self,
                                            self.map[x][y],
                                            self.map[x][y].custom['preset'])
                    self.tribes.append(tribe_ref)

        assert len(self.tribes), 'No tribes found at map'
        self.active_tribe = self.tribes[0]

        self.PathFinder = path_finder.PathFinder(self.map)

        return None

    def blit_map(self):
        '''
        Blits entire landscape on the Screeen.
        ??? should be implementet priority for objects and landscape animation
        '''
        for x in range(0,LAND_NUM_X):
            for y in range(0,LAND_NUM_Y):
                self.map[x][y].blit(self.ScreenSurface)

        self.ClearLandscape = self.ScreenSurface.copy()

        return None

    def clear_map(self):
        '''
        Blits native landscape in rectangles where sprites were blited.
        '''
        for obj in self.active_sprites:
            self.ScreenSurface.blit(self.ClearLandscape, obj.Rect, obj.Rect)

        return None

    def environment_update(self):
        '''
        (None) -> None

        Activities that should be performed in the end of the day or night.
        '''
        # Resource regeneration
        for x in range(0,LAND_NUM_X):
            for y in range(0,LAND_NUM_Y):
                self.map[x][y].regenerate()

        return None

    def process_sprites(self):
        '''
        Updates displayed frame and position for all sprites and remove ones
        that are not visible any more.
        '''
        
        for obj in self.active_sprites[:]:
            if obj.visible == False:
                self.active_sprites.remove(obj)
                
        for obj in self.active_sprites:
            obj.move()

        return None

    def blit_sprites(self):
        '''
        Blits all sprites that should be displayed.
        ??? should be implemented priority for objects and landscape animation
        '''
        for obj in self.active_sprites:
            obj.blit(self.ScreenSurface)

        return None

    def flow(self):
        '''
        (None) -> None

        Control and change of game phase and mode
        There are 3 game phases:
            - generate_parties - players forms parties for activities
            - send - tribesmen went to work
            - day - parties goes to location and performs some activities
            - return - tribesmen went home
            - evening - parties returns back home and eats
        '''

        all_done_flag = True
        for tribe in self.tribes:
            if not tribe.ready:
                if self.game_phase == MORNING:
                    if len(tribe.get_free_tribesmen()) > 0:
                        self.active_tribe = tribe
                        tribe.morning()
                elif self.game_phase == SEND:
                    tribe.send_parties()
                elif self.game_phase == DAY:
                    tribe.day()
                    tribe.build_send_query(home=True)
                elif self.game_phase == RETURN:
                    tribe.send_parties()
                elif self.game_phase == EVENING:
                    tribe.everning()
                all_done_flag = False
        if all_done_flag:
            self._next_game_phase()



        return None

    def _next_game_phase(self):
        '''
        (None) -> None

        Sets next game phase. When last phase is reached - sets firs one.
        '''
        if self.game_phase == 4:
            #Turn is over
            self.environment_update()
            self.move_counter += 1
            print('Move #',self.move_counter,'is over.')
        self.game_phase += 1
        if self.game_phase > 4:
            self.game_phase = 0
        print('Game phase:',self.game_phase)
        self.update = True
        for tribe in self.tribes:
            tribe.ready = False

        return None

    def check_popups(self):
        '''
        (None) -> bool

        Checks if popup is required to be displayed by Core or any tribe.
        '''

        if self.popup:
            self.update = True
            return True
        for tribe in self.tribes:
            if tribe.popup:
                self.update = True
                return True

        return None
    






















        
        
