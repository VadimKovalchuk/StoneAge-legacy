from source import tools
from source import land_cell
from source import tribe
from source import path_finder
from source import rules
from source import textprocessor

#CONSTANTS
#Uplading constants from setup.ini file

constants = tools.Constants()
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
        (Surface, Scenarion) -> None

        Loads map via scenario and builds it with land cells
        '''

        self.ScreenSurface = ScreenSurface
        self.ClearLandscape = ScreenSurface.copy()
        self.Scenario = Scenario
        self.Loader = Loader
        self.map = []
        self.tribes = []
        self.active_tribe = None
        self.active_sprites = []

        self.PathFinder = None
        self.Logger = tools.Logger()
        self.Rules = rules.Rules(self)
        self.Txt = textprocessor.TextProcessor()

        self.game_mode = 'regular'
        self.game_phase = 0
        self.move_counter = 0
        self.update = False
        self.popup = {}
        self.raise_popup = False
        self.marker_tasks = {'refresh':[],'remit':[]}

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
        self.map[0][0].markers.append('selection')
        self.marker_tasks['refresh'].append(self.map[0][0])

        self.PathFinder = path_finder.PathFinder(self.map)

        return None

    def blit_map(self):
        '''
        Blits entire landscape on the Screen.
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
            self.ScreenSurface.blit(self.ClearLandscape, obj.rect, obj.rect)

        for cell in self.marker_tasks['remit'][:]:
            self.ScreenSurface.blit(self.ClearLandscape, cell.rect, cell.rect)
            self.marker_tasks['remit'].remove(cell)
            if len(cell.markers):
                cell.blit_markers(self.ScreenSurface)

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
            if not obj.visible:
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

        for cell in self.marker_tasks['refresh'][:]:
            cell.blit_markers(self.ScreenSurface)
            self.marker_tasks['refresh'].remove(cell)

        return None

    def update_markers(self, all=False):
        '''
        (None) -> None

        Verifies if any markers should be active for land cell.
        If necessary activates them, and remits.
        Also refreshes them in case of collision with sprite.
        '''
        def _check_activity(cell):
            '''
            (None) -> None

            Enables activity marker when tribesmen enters wild location cell
            and remits it when everybody leaves it.
            '''
            if cell.land_type == 'camp':
                return None
            if self.game_phase == SEND:
                if 'activity' in cell.markers:
                    return None
                for tribee in self.tribes:
                    for man in tribee.population:
                        if not man.visible and man.cell == cell.cell:
                            cell.markers.append('activity')
                            return None
            elif self.game_phase == RETURN:
                if 'activity' not in cell.markers:
                    return None
                remit = True
                for tribee in self.tribes:
                    for man in tribee.population:
                        if (man not in self.active_sprites) and\
                                man.cell == cell.cell:
                            remit = False
                if remit:
                    cell.markers.remove('activity')
                    self.marker_tasks['remit'].append(cell)
            return None


        for x in range(0,LAND_NUM_X):
            for y in range(0,LAND_NUM_Y):
                if all:
                    self.marker_tasks['refresh'].append(self.map[x][y])
                _check_activity(self.map[x][y])
                if len(self.map[x][y].markers) and \
                        (self.map[x][y] not in self.marker_tasks['refresh']):
                    for sprite in self.active_sprites:
                        if self.map[x][y].rect.colliderect(sprite.rect):
                            self.marker_tasks['refresh'].append(self.map[x][y])

        return None

    def set_selected_cell(self, old, new):
        '''
        ((int,int)) -> None

        Remits "selected" marker from old cell and sets it for new one
        '''
        x,y = old
        self.map[x][y].markers.remove('selection')
        self.marker_tasks['remit'].append(self.map[x][y])
        x,y = new
        self.map[x][y].markers.append('selection')
        self.marker_tasks['refresh'].append(self.map[x][y])

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
        self.update_markers()
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
        self.check_popups()



        return None

    def _next_game_phase(self):
        '''
        (None) -> None

        Sets next game phase. When last phase is reached - sets firs one.
        '''
        if self.game_phase == EVENING:
            #Turn is over, updates at the end of the day are applied.
            self.environment_update()
            self.move_counter += 1
            print('Move #',self.move_counter,'is over.')

        self.game_phase += 1
        if self.game_phase > 4:
            self.game_phase = 0
        print('Game phase:',self.game_phase)

        if self.game_phase == MORNING:
            #New turn starts, updates at the beginning of the day are applied.
            for tribe in self.tribes:
                self.Rules.treat_fire(tribe)
        self.update = True
        for tribe in self.tribes:
            tribe.ready = False

        return None

    def check_popups(self):
        '''
        (None) -> bool

        Checks if popup is required to be displayed by Core or any tribe.
        '''

        if self.popup and self.raise_popup:
            self.update = True
            return True
        for tribe in self.tribes:
            if tribe.popup and tribe.raise_popup:
                self.update = True
                return True

    






















        
        
