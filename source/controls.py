import pygame

#CONSTANTS
#Uplading constants from setup.ini file
from source import tools, party

constants = tools.importConstants()
'''___________________________________________________________'''
#Set up window resolution
WINDOW_WIDTH    = constants['WINDOW_WIDTH']     #Default 1280
WINDOW_HEIGHT   = constants['WINDOW_HEIGHT']    #Default 720
#Side(control) panel and game field width
SIDE_PANEL_WIDTH= constants['SIDE_PANEL_WIDTH'] #Calculated
FIELD_WIDTH = constants['FIELD_WIDTH']          #Calculated
#Used colors
BROWN           = constants['BROWN']            #Optional
ORANGE          = constants['ORANGE']           #Optional
#Resource richness in land cell
EMPTY = constants['EMPTY']      #Default is 'empty'
LOW = constants['LOW']          #Default is 'low'
MODERATE = constants['MODERATE']#Default is 'moderate'
MANY = constants['MANY']        #Default is 'many'
RICH = constants['RICH']        #Default is 'rich'

del constants

BUTTON_SIZE = 35
LINE_WIDTH = 2
FIRST_TEXT_COLUMN = (int(BUTTON_SIZE *1.1), BUTTON_SIZE // 3)
SECOND_BUTTON_COLUMN = int(BUTTON_SIZE *2.5)
SECOND_TEXT_COLUMN = (int(BUTTON_SIZE *3.6), BUTTON_SIZE // 3)

#Buttons
YES = 'yes'
NO = 'no'
PROCESS_MAN =  'process_man'
PROCESS_FOOD = 'process_food'
PROCESS_SKIN = 'process_skin'
PROCESS_HEAL = 'process_heal'
GET_FOOD = 'get_food'
GET_HUNT = 'get_hunt'
GET_WOOD = 'get_wood'
GET_STONE = 'get_stone'
FORM_PARTY = [PROCESS_MAN, PROCESS_FOOD, PROCESS_SKIN,PROCESS_HEAL,
              GET_FOOD, GET_HUNT, GET_WOOD, GET_STONE]
'''___________________________________________________________'''

class Controls:
    """ Controls handles pygame input events. Performs task asignment
       for map and tribe for next move """

    def __init__(self, ScreenSurface, Core, Loader):
        '''
        (self, Surface, Map) -> NoneType

        '''

        self.ScreenSurface = ScreenSurface
        self.Loader = Loader
        self.Core = Core
        self.Tribe = Core.active_tribe
        self.selected = self.Core.map[0][0]
        self.pause = False
        self.update = True
        self.buttons = []
        self.menu_mode = 'general'
        self.called_method = ''
        self.Party = None
        self.party_list = []
        self.free_list = []

        #Internal variables
        self.HeaderText = pygame.font.SysFont(None, 24)
        self.RegularText = pygame.font.SysFont(None, 20)
        self.richness_image_for = {
            EMPTY:   'red_circle_icon',
            LOW:     'red_circle_icon',
            MODERATE:'yellow_circle_icon',
            MANY:    'green_circle_icon',
            RICH:    'blue_circle_icon'
        }
        self.cell_image_for = {
            'food': 'apple_button',
            'wood': 'wood_button',
            'stone':'stone_button',
            'hunt': 'meat_button'
        }
        self.weapon_image_for = {
            'unarmed':      'unarmed_button',
            'bone_knife':   'bone_knife_button',
            'spear':        'spear_button',
            'bone_spear':   'bone_spear_button',
            'stone_spear':  'stone_spear_button',
            'stone_axe':    'stone_axe_button'
        }
        self.armor_image_for = {
            'undressed':     'undressed_button',
            'light_leather': 'light_leather_button',
            'medium_leather':'medium_leather_button',
            'heavy_leather': 'heavy_leather_button',
            'bone_armor':    'bone_armor_button'
        }
        self.menu_line = [WINDOW_WIDTH - SIDE_PANEL_WIDTH + \
                                    LINE_WIDTH * 4, LINE_WIDTH * 4]
        self.block_topleft = [0,0]
        self.block_height = 0
        

        return None

    def blit_all(self):
        '''
        (self) -> NoneType

        Blits whole side menu from the scratch
        '''
        self.Tribe = self.Core.active_tribe
        self.buttons = []
        self._blit_background()
        #Verification for required popup display
        if self.menu_mode == 'general' and self.Core.check_popups():
            self.menu_mode = 'popup'

        #Blits menu components
        if self.menu_mode == 'general':
            self._blit_cell_menu()
            self._blit_tribe_menu()
        elif self.menu_mode == 'party_builder':
            self._party_builder_parser()
            self._party_builder_menu()
        elif self.menu_mode == 'popup':
            pass
        else:
            assert False, 'Incorrect menu mode'

        self.update = False
        self.Core.update = False

        return None

    def _blit_background(self):
        '''
        (None) -> none

        Blits background image adn frame around it.
        '''

        self.ScreenSurface.blit(self.Loader.controls['menu_background'],
                                ((WINDOW_WIDTH - SIDE_PANEL_WIDTH,0),
                                 (SIDE_PANEL_WIDTH,WINDOW_HEIGHT)))
        #Blits frame around side menu edge
        self._blit_frame(WINDOW_WIDTH - SIDE_PANEL_WIDTH,  0,
                       SIDE_PANEL_WIDTH, WINDOW_HEIGHT)

        self.menu_line = [WINDOW_WIDTH - SIDE_PANEL_WIDTH +\
                                 LINE_WIDTH * 2, LINE_WIDTH * 2]

        return None

    def _blit_cell_menu(self):
        '''
        (self) -> NoneType

        Blits land cell info section
        '''
        self._prepare_menu()

        self._blit_text(self.selected.land_type.capitalize(), 'header')
        self._next_line(self.HeaderText.get_height())

        if self.Core.PathFinder.get_path(self.Tribe.home_cell.cell,self.selected.cell):
            # Creates and blits button for each resource that higher than 0
            for resource in self.selected.resources:
                if self.selected.resources[resource] == 0:
                    continue
                # Blits button which creates the party for specific resource
                self._create_button(self.cell_image_for[resource],'get_' + resource)

                # Blits resource richness
                richness = self.selected.richness(resource)
                self._blit_icon(self.richness_image_for[richness],FIRST_TEXT_COLUMN[0])

                #Blits resource cost
                cost_table = self.Core.Rules.resource_cost_matrix
                land_type = self.selected.land_type
                cost = cost_table[land_type][resource]
                self._blit_icon('point_icon',SECOND_BUTTON_COLUMN)
                self._blit_text('x '+str(cost),'header',SECOND_TEXT_COLUMN)

                self._next_line()
        else:
            self._blit_text('Location is not reachable', 'regular')
            self._next_line(self.HeaderText.get_height())

        self._compleate_menu()

        return None

    def _blit_tribe_menu(self):
        '''
        (self) -> NoneType

        Blits tribe menu section
        '''


        self._prepare_menu()

        self._blit_text(self.Tribe.name, 'header')
        self._next_line(self.HeaderText.get_height())

        self._create_button('tribesman_button',PROCESS_MAN)
        self._blit_text('x ' + str(len(self.Tribe.population)),
                        'header', FIRST_TEXT_COLUMN)
        self._create_button('heal_button',PROCESS_HEAL,SECOND_BUTTON_COLUMN)
        self._next_line()

        self._blit_icon('meat_icon')
        self._blit_text('x ' + str(self.Tribe.get_resource('food')),
                        'header', FIRST_TEXT_COLUMN)

        self._create_button('stocked_button',PROCESS_FOOD,
                            offset=SECOND_BUTTON_COLUMN)
        self._blit_text('x ' + str(self.Tribe.get_resource('stocked_food')),
                        'header', SECOND_TEXT_COLUMN)
        self._next_line()

        self._blit_icon('bone_icon')
        self._blit_text('x ' + str(self.Tribe.get_resource('bones')),
                        'header', FIRST_TEXT_COLUMN)
        self._next_line()

        self._blit_icon('moist_skin_icon')
        self._blit_text('x ' + str(self.Tribe.get_resource('moist_skin')),
                        'header', FIRST_TEXT_COLUMN)

        self._create_button('skin_button',PROCESS_SKIN,
                            offset=SECOND_BUTTON_COLUMN)
        self._blit_text('x ' + str(self.Tribe.get_resource('skin')),
                        'header', SECOND_TEXT_COLUMN)
        self._next_line()

        self._blit_icon('wood_icon')
        self._blit_text('x ' + str(self.Tribe.get_resource('wood')),
                        'header', FIRST_TEXT_COLUMN)
        self._next_line()

        self._blit_icon('stone_icon')
        self._blit_text('x ' + str(self.Tribe.get_resource('stone')),
                        'header', FIRST_TEXT_COLUMN)
        self._next_line()

        self._compleate_menu()

        return None

    def _party_builder_menu(self):
        '''
        (self) -> NoneType

        Blits tribe menu section
        '''
        self._prepare_menu()

        valid_party = self.Party.is_valid(self.Tribe)
        if valid_party is not None:
            self._blit_text(valid_party, 'regular')
            self._next_line(self.HeaderText.get_height())

        self._blit_tribesmen_list(self.party_list,'remove_from_party_')
        self._blit_delimiter()
        self._blit_tribesmen_list(self.free_list,'add_to_party_')

        self._blit_delimiter()
        self._create_button('yes_button', YES)
        offset = SIDE_PANEL_WIDTH - BUTTON_SIZE - LINE_WIDTH * 8
        self._create_button('no_button', NO, offset)
        self._next_line()

        self._compleate_menu()

        return None

    def _blit_tribesmen_list(self, tribesmen_list, command):
        '''
        (list) -> None

        Blits list of tribesmen for _party_builder_menu
        '''
        text_offset = (int(BUTTON_SIZE *1.1), BUTTON_SIZE // 3)
        counter = 0
        for tribesman in tribesmen_list:
            self._create_button('tribesman_button',command + str(counter))
            self._blit_text(tribesman.name, 'header',text_offset)
            self._blit_health_points(tribesman)

            counter += 1
            self._next_line()


        return None

    def _blit_frame(self, x, y, width, height):
        '''
        (self, int, int, int, int) -> NoneType

        Blits frame as delimiter and a button visualisation
        '''
        width = width - LINE_WIDTH
        height = height - LINE_WIDTH
        
        pygame.draw.line(self.ScreenSurface, BROWN,
                        (x, y), (x + width, y), LINE_WIDTH)
        pygame.draw.line(self.ScreenSurface, BROWN,
                        (x, y + height),
                        (x + width, y + height), LINE_WIDTH)
        pygame.draw.line(self.ScreenSurface, BROWN,
                        (x, y), (x, y + height), LINE_WIDTH)
        pygame.draw.line(self.ScreenSurface, BROWN,
                        (x + width, y),
                        (x + width, y + height), LINE_WIDTH)

        
        return None

    def _blit_delimiter(self):
        '''
        (None) -> None

        Blits horizontal delimiter line.
        '''
        left_point = [self.menu_line[0]+ BUTTON_SIZE // 3,
                      self.menu_line[1]+ BUTTON_SIZE // 2]
        right_point = left_point[:]
        right_point[0] += SIDE_PANEL_WIDTH - BUTTON_SIZE
        pygame.draw.line(self.ScreenSurface, BROWN,
                        left_point, right_point, LINE_WIDTH)
        self._next_line()

        return None

    def _blit_text(self, text, type, offset = (0,0),
                   bold = False, coordinates = None):
        '''
        (self, str, (int, int), (int, int), bool) -> NoneType

        Blits text. If 'bold' passed as True than bold text will be blited.
        '''

        if bold == True:
            self.HeaderText.set_bold(True)
            self.RegularText.set_bold(True)

        if type == 'header':
            text_line = self.HeaderText.render(str(text), True, (0,0,0))
        elif type == 'regular':
            text_line = self.RegularText.render(str(text), True, (0,0,0))
        text_rect = text_line.get_rect()

        if not coordinates:
            coordinates = self.menu_line
        text_rect.left = coordinates[0] + offset[0]
        text_rect.top = coordinates[1] + offset[1]

        self.ScreenSurface.blit(text_line, text_rect)

        if bold == True:
            self.HeaderText.set_bold(False)
            self.RegularText.set_bold(False)

        return None

    def _next_line(self,increment = BUTTON_SIZE):
        '''
        (self) -> NoneType

        Changes self.menu_line value to draw next line of buttons
        and extends total size of builded block. Dependency from BUTTON_SIZE.
        '''

        increment = int(increment * 1.1)
        self.menu_line[1] += increment
        self.block_height += increment

        return None

    def _prepare_menu(self):
        '''
        (self) -> NoneType

        Setting menu variables(self.block_topleft, self.next_line)
        for elements placement and final menu frame bliting
        '''
        self.block_height = 0
        self.block_topleft[0] = self.menu_line[0]
        self.block_topleft[1] = self.menu_line[1]
        self.menu_line[0] += LINE_WIDTH * 2
        self.menu_line[1] += LINE_WIDTH * 2

        return None

    def _compleate_menu(self):
        '''
        (self) -> NoneType
        '''
        self._blit_frame( self.block_topleft[0], self.block_topleft[1],
                        SIDE_PANEL_WIDTH - LINE_WIDTH * 4,
                        self.block_height + LINE_WIDTH * 2)

        self.menu_line[0] = self.block_topleft[0]
        self.menu_line[1] += LINE_WIDTH

        return None

    def _create_button(self, image, method, offset=0):
        '''
        (self, Surface, str, int) -> NoneType

        Blits button at current line with defined picture and offset in px
        to left. Creates instance of Button class and adds it in the buttons
        list.
        '''

        draw_rect = self.Loader.controls[image].get_rect()
        draw_rect.top = self.menu_line[1]
        draw_rect.left = self.menu_line[0] + offset
        self.ScreenSurface.blit(self.Loader.controls[image],
                                 draw_rect)
        self._blit_frame(draw_rect.x, draw_rect.y,
                         draw_rect.width, draw_rect.height)
        button_dict = {'rect':draw_rect, 'method':method}
        self.buttons.append(button_dict)

        return None

    def _blit_icon(self, image, offset=0):
        '''
        (self, Surface, str, int) -> NoneType

        Blits button at current line with defined picture and offset in px
        to left. Creates instance of Button class and adds it in the buttons
        list.
        '''

        draw_rect = self.Loader.controls[image].get_rect()
        draw_rect.top = self.menu_line[1]
        draw_rect.left = self.menu_line[0] + offset
        self.ScreenSurface.blit(self.Loader.controls[image],
                                 draw_rect)

        return None

    def _blit_richness(self, resource, offset= 0):
        '''
        (str,(int,int)) -> None

        Blits resource richness for selected land cell.
        '''

        return None

    def _blit_health_points(self, tribesman):
        '''
        (tribesman) -> None

        Blits tribesman health points.
        '''
        self._blit_icon('point_icon',SECOND_BUTTON_COLUMN)
        self._blit_text('x' + str(tribesman.points),'header',SECOND_TEXT_COLUMN)

        return None

    def _blit_weapon(self, tribesman, offset= 0):
        '''
        (tribesman) -> None

        Blits tribesman weapon.
        !!!In current implementation only as icon.
        '''

        return None

    def _blit_armor(self, tribesman, offset= 0):
        '''
        (tribesman) -> None

        Blits tribesman armor.
        !!!In current implementation only as icon.
        '''

        return None

    def mouseInput(self, position):
        '''
        (self, (int, int)) -> None

        Handles mouse input
        '''
        if position[0] >= FIELD_WIDTH:
            for button in self.buttons:
                if button['rect'].collidepoint(position):
                    self.called_method = button['method']
                    self.update = True
                    # If action requires selection for some amount of tribesmen
                    # than party builder menu is generated
                    if self.called_method in FORM_PARTY:
                        self.menu_mode = 'party_builder'
                        self.Party = party.Party(self.Tribe, self.selected.cell,
                                                 button['method'])
                        self.free_list = self.Tribe.get_free_tribesmen()

                        print('Defined parties:')
                        for defined_party in self.Tribe.parties:
                            print('\t' + str(defined_party))

                    #Handles results from all menus with YES
                    elif self.called_method == YES:
                        #YES for party builder
                        if self.menu_mode == 'party_builder' and\
                                not self.Party.is_valid(self.Tribe):
                            self.Tribe.parties.append(self.Party)
                            print('Created party:', self.Party)
                            self.party_list = []
                            self.menu_mode = 'general'
                            if len(self.Tribe.get_free_tribesmen()) == 0 and \
                                    len(self.Tribe.send_query) == 0 and \
                                    len(self.Tribe.parties) > 0:
                                self.Tribe.build_send_query()

                    #Handles results from all menus with NO
                    elif self.called_method == NO:
                        #NO for party builder
                        if self.menu_mode == 'party_builder':
                            del self.Party
                            self.party_list = []
                            self.menu_mode = 'general'


        else:
            (x,y) = tools.pxToCellCoordinate(position)
            self.selected = self.Core.map[x][y]
            self.update = True
            print((x,y))

        return None



    def _party_builder_parser(self):
        '''
        (self) -> NoneType

        Parses command in self.called_method generated by party builder menu
        and applies them
        '''
        if 'add_to_party' in self.called_method:
            if self.called_method[-2].isnumeric():
                index = int(self.called_method[-2:])
            else:
                index = int(self.called_method[-1])
            self.party_list.append(self.free_list.pop(index))
        elif 'remove_from_party' in self.called_method:
            if self.called_method[-2].isnumeric():
                index = int(self.called_method[-2:])
            else:
                index = int(self.called_method[-1])
            self.free_list.append(self.party_list.pop(index))
        self.Party.members = self.party_list[:]

        return None
















