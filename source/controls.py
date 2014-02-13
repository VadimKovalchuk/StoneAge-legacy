import pygame

#CONSTANTS
#Uplading constants from setup.ini file
from source import tools, party

constants = tools.importConstants()
'''___________________________________________________________'''
#Set up window resolution
WINDOW_WIDTH    = constants['WINDOW_WIDTH']     #Default 1280
WINDOW_HEIGHT   = constants['WINDOW_HEIGHT']    #Default 720
#Loader image categories
CONTROLS    = constants['CONTROLS']     #Default is 'controls'
ICON        = constants['ICON']         #Default is 'icon'
BUTTON      = constants['BUTTON']       #Default is 'button'
POPUP       = constants['POPUP']        #Default is 'popup'
BACKGROUND  = constants['BACKGROUND']   #Default is 'background'
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
MENU_COLUMNS = [(0,BUTTON_SIZE // 3),
               (int(BUTTON_SIZE *1.1),BUTTON_SIZE // 3),
               (int(BUTTON_SIZE *2.2),BUTTON_SIZE // 3),
               (int(BUTTON_SIZE *3.3),BUTTON_SIZE // 3),
               (int(BUTTON_SIZE *4.4),BUTTON_SIZE // 3),
               (int(SIDE_PANEL_WIDTH - LINE_WIDTH * 8 - BUTTON_SIZE),BUTTON_SIZE // 3)]

#Buttons
SUBMODE = 'submode'
YES = 'yes'
NO = 'no'
PROCESS_MAN =  'process_man'
PROCESS_FOOD = 'process_food'
PROCESS_SKIN = 'process_skin'
PROCESS_HEAL = 'process_heal'
PROCESS_SKILL = 'process_skill'
GET_FOOD = 'get_food'
GET_HUNT = 'get_hunt'
GET_WOOD = 'get_wood'
GET_STONE = 'get_stone'
SKILLS_MENU = 'skills_menu'
FORM_PARTY = [PROCESS_MAN, PROCESS_FOOD, PROCESS_SKIN,PROCESS_HEAL,
              GET_FOOD, GET_HUNT, GET_WOOD, GET_STONE]
#Popup
POPUP_RECT = ((FIELD_WIDTH // 4,WINDOW_HEIGHT // 4),
              (FIELD_WIDTH // 2, WINDOW_HEIGHT //2))
POPUP_PIC =  ((POPUP_RECT[0][0] + 40, POPUP_RECT[0][1] + 20),
               (150,320))
POPUP_TXT_INDENT = (200,40)
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
        self.Txt = self.Core.Txt
        self.selected = self.Core.map[0][0]
        self.pause = False
        self.update = True
        self.buttons = []
        self.menu_mode = 'general'
        self.menu_submode = ''
        self.popup_obj = None
        self.called_method = ''
        self.Party = None
        self.party_list = []
        self.free_list = []

        #Internal variables
        self.HeaderText = pygame.font.SysFont(None, 24)
        self.RegularText = pygame.font.SysFont(None, 20)
        self.richness_image_for = {
            EMPTY:   'red_circle',
            LOW:     'red_circle',
            MODERATE:'yellow_circle',
            MANY:    'green_circle',
            RICH:    'blue_circle'
        }
        self.cell_image_for = {
            'food': 'apple',
            'wood': 'wood',
            'stone':'stone',
            'hunt': 'meat',
            'bones': 'bone'
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

    def refresh(self):
        '''
        (None) -> None
        '''
        if self.update or self.Core.update or self.Core.raise_popup \
            or self.Tribe != self.Core.active_tribe:
            self._blit_all()

        return None

    def _blit_all(self):
        '''
        (self) -> NoneType

        Blits whole side menu from the scratch
        '''
        self.Tribe = self.Core.active_tribe
        self.buttons = []
        self._blit_background()
        #Verification for popup display request
        self._popup_required()

        #Blits menu components
        if self.menu_mode == 'general':
            self._blit_cell_menu()
            self._blit_tribe_menu()
        elif self.menu_mode == 'party_builder':
            self._party_builder_menu()
        elif self.menu_mode == 'popup':
            self._blit_popup()
        elif self.menu_mode == SKILLS_MENU:
            self._blit_skills_menu()
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

        self.ScreenSurface.blit(self.Loader.get(BACKGROUND,'menu'),
                                ((WINDOW_WIDTH - SIDE_PANEL_WIDTH,0),
                                 (SIDE_PANEL_WIDTH,WINDOW_HEIGHT)))
        #Blits frame around side menu edge
        self._blit_frame(WINDOW_WIDTH - SIDE_PANEL_WIDTH,  0,
                       SIDE_PANEL_WIDTH, WINDOW_HEIGHT)

        self.menu_line = [WINDOW_WIDTH - SIDE_PANEL_WIDTH +\
                                 LINE_WIDTH * 2, LINE_WIDTH * 2]

        return None

    def _popup_required(self):
        '''
        (None) -> None

        Verifies if popup is required and prepares data for display.
        '''
        if self.Core.check_popups():
            self.menu_mode = POPUP
            #For which object popup should be raised
            for tribe in self.Core.tribes:
                if tribe.raise_popup:
                    self.popup_obj = tribe
            if self.Core.raise_popup:
                self.popup_obj = self.Core

        return None

    def _blit_cell_menu(self):
        '''
        (self) -> NoneType

        Blits land cell info section
        '''
        self._prepare_menu()

        self._blit_text(self.selected.land_type, 'header')
        self._next_line(self.HeaderText.get_height())

        if self.Core.PathFinder.get_path(self.Tribe.home_cell.cell,self.selected.cell):
            # Creates and blits button for each resource that higher than 0
            for resource in self.selected.resources:
                if self.selected.resources[resource] == 0:
                    continue
                # Blits button which creates the party for specific resource
                self._blit_button(self.cell_image_for[resource],'get_' + resource)

                # Blits resource richness
                richness = self.selected.richness(resource)
                self._blit_icon(self.richness_image_for[richness],FIRST_TEXT_COLUMN[0])

                #Blits resource cost
                cost_table = self.Core.Rules.resource_cost_matrix
                land_type = self.selected.land_type
                cost = cost_table[land_type][resource]
                if resource == 'hunt':
                    img = 'hit_point'
                else:
                    img = 'point'
                self._blit_icon(img,SECOND_BUTTON_COLUMN)
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

        self._blit_button('tribesman',PROCESS_MAN)
        self._blit_text('x ' + str(len(self.Tribe.population)),
                        'header', FIRST_TEXT_COLUMN)
        self._blit_button('heal',PROCESS_HEAL,SECOND_BUTTON_COLUMN)
        self._blit_button('inventory',PROCESS_FOOD,
                            MENU_COLUMNS[-1][0])
        self._next_line()

        self._blit_icon('meat')
        self._blit_text('x ' + str(self.Tribe.get_resource('food')),
                        'header', FIRST_TEXT_COLUMN)

        self._blit_button('stocked',PROCESS_FOOD,
                            offset=SECOND_BUTTON_COLUMN)
        self._blit_text('x ' + str(self.Tribe.get_resource('stocked_food')),
                        'header', SECOND_TEXT_COLUMN)
        self._next_line()

        self._blit_icon('bone')
        self._blit_text('x ' + str(self.Tribe.get_resource('bones')),
                        'header', FIRST_TEXT_COLUMN)
        self._blit_button('workshop',PROCESS_FOOD,
                            offset=SECOND_BUTTON_COLUMN)
        #self._blit_icon('question',SECOND_TEXT_COLUMN[0])
        self._next_line()

        self._blit_icon('moist_skin')
        self._blit_text('x ' + str(self.Tribe.get_resource('moist_skin')),
                        'header', FIRST_TEXT_COLUMN)

        self._blit_button('skin',PROCESS_SKIN,
                            offset=SECOND_BUTTON_COLUMN)
        self._blit_text('x ' + str(self.Tribe.get_resource('skin')),
                        'header', SECOND_TEXT_COLUMN)
        self._next_line()

        self._blit_icon('wood')
        self._blit_text('x ' + str(self.Tribe.get_resource('wood')),
                        'header', FIRST_TEXT_COLUMN)
        self._next_line()

        self._blit_icon('stone')
        self._blit_text('x ' + str(self.Tribe.get_resource('stone')),
                        'header', FIRST_TEXT_COLUMN)
        self._blit_button('wheel',SKILLS_MENU,offset=SECOND_BUTTON_COLUMN)
        self._next_line()

        self._compleate_menu()

        return None

    def _party_builder_menu(self):
        '''
        (self) -> NoneType

        Blits tribe menu section
        '''

        def _party_builder_parser():
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

        def _blit_tribesmen_list(tribesmen_list, command):
            '''
            (list) -> None

            Blits list of tribesmen for _party_builder_menu
            '''
            text_offset = (int(BUTTON_SIZE *1.1), BUTTON_SIZE // 3)
            counter = 0
            for tribesman in tribesmen_list:
                self._blit_button('tribesman',command + str(counter))
                self._blit_text(tribesman.name, 'header',text_offset)
                if self.menu_submode == 'points':
                    self._blit_health_points(tribesman)
                elif self.menu_submode == 'equip':
                    self._blit_equip(tribesman)
                counter += 1
                self._next_line()
            return None

        def _submode_switch_button():
            '''
            (None) -> None

            Blits button for menu submode switching.
            '''
            if self.menu_submode == 'points':
                mode_image = 'hit_point'
            elif self.menu_submode == 'equip':
                mode_image = 'point'
            self._blit_button(mode_image,SUBMODE,FIRST_TEXT_COLUMN[0])

            return None

        _party_builder_parser()
        self._prepare_menu()

        valid_party = self.Party.is_valid(self.Tribe)
        if valid_party:
            output_text = self.Txt.get_txt('controls', valid_party)
            self._blit_text(output_text, 'regular')
            self._next_line(self.HeaderText.get_height())

        _blit_tribesmen_list(self.party_list,'remove_from_party_')
        self._blit_delimiter()
        _blit_tribesmen_list(self.free_list,'add_to_party_')

        self._blit_delimiter()
        self._blit_button('yes', YES)
        _submode_switch_button()
        self._blit_button('no', NO, MENU_COLUMNS[-1][0])
        self._next_line()

        self._compleate_menu()

        return None

    def _blit_popup(self):
        '''
        (None) -> None

        Blits popup.
        '''

        def _blit_popup_text(text, line):
            '''
            (str, int) -> None

            Blits text until '\n' character and calls itself with the
            remaining text until text is over. Passed lint is drawn
            with corresponding offset.
            '''
            if len(text) == 0:
                return None
            index = text.find('\n')
            text_img = self.RegularText.render(text[:index], True, (0,0,0))
            text_rect = text_img.get_rect()
            text_rect.left = POPUP_RECT[0][0] + POPUP_TXT_INDENT[0]
            text_rect.top = POPUP_RECT[0][1] + POPUP_TXT_INDENT[1] + line * 20
            self.ScreenSurface.blit(text_img, text_rect)
            if index == -1:
                return None
            _blit_popup_text(text[index + 1:], line + 1)

            return None

        def _popup_pic():
            '''
            (None) -> str

            Gets picture that should be blited for current popup.
            '''
            if 'picture' in self.popup_obj.popup:
                return self.popup_obj.popup['picture']
            else:
                return self.popup_obj.popup['type'][0]

        self.pause = True
        self.ScreenSurface.blit(self.Loader.get('background','popup'),
                                POPUP_RECT)
        self.ScreenSurface.blit(self.Loader.get(POPUP,_popup_pic()),POPUP_PIC)
        popup_text = self.Txt.popup(self.popup_obj)
        _blit_popup_text(popup_text,1)
        # Popup button
        self._prepare_menu()
        self._blit_button('yes', YES)
        self._blit_text('Done',
                        'header', FIRST_TEXT_COLUMN)
        self._next_line()
        self._compleate_menu()

        return None

    def _blit_skills_menu(self):
        '''
        (None) -> None

        Blits Skills Menu.
        '''
        def _command_handler():
            '''
            (None) -> None

            Handles called method and changes Skill menu content according to it
            '''
            if 'skill' in self.called_method:
                if 'info' in self.called_method:
                    skill_id = int(self.called_method[-3:])
                    self.Core.popup = {'type':['skill_info'],
                                       'skill':skill_id,
                                       'picture':'skill' + str(skill_id)}
                    self.Core.raise_popup = True
                    self.Core.update = True
                    self.update = True
                elif self.called_method[-3:].isnumeric():
                    skill_id = int(self.called_method[-3:])
                    for skill in self.Tribe.SkillTree.available_skills:
                        if skill.id == skill_id:
                            self.Tribe.SkillTree.learned = skill
                            break

            return None

        def _number_to_str(number):
            '''
            (int) -> str

            Transform number in range 0..999 into string but always with three digits.
            '''
            if number < 10:
                return '00' + str(number)
            elif number < 100:
                return '0' + str(number)
            else:
                return str(number)

        def _blit_requirements(skill,req):
            '''
            (Skill, dict) -> None

            Blits Skill as an icon and requirements for its study. Help button
            is also added for Skill.
            '''
            self._blit_icon('skill' + str(skill.id))
            self._blit_icon(self.cell_image_for[req['resource']],
                            MENU_COLUMNS[1][0])
            txt = str(req['obtained']) + '/' + str(req['required'])
            self._blit_text(txt,'header',MENU_COLUMNS[2])


            return None

        def _blit_ready(skill):
            '''
            (Skill) -> None

            Blits Skill as a button when required experience is gained.
            '''
            self._blit_button('skill' + str(skill.id), 'skill' + _number_to_str(skill.id))
            return None

        def _blit_selected(skill):
            '''
            (Skill) -> None

            Blits selected Skill separately as an icon and its price.
            '''
            self._blit_icon('skill' + str(skill.id))
            price = skill.get_price()
            counter = 0
            for resource in price:
                self._blit_icon(self.cell_image_for[resource],
                                MENU_COLUMNS[counter * 2 + 1][0])
                self._blit_text('x' + str(price[resource]),'header',
                                MENU_COLUMNS[counter * 2 + 2])
                counter += 1
                if counter > 1:
                    self._next_line()
                    counter = 0

            return None

        def _yes_conditions():
            '''
            (None) -> None

            Verifies conditions for YES button to blit. If conditions are
            not satisfied blits grayed out YES icon.
            '''
            if self.Tribe.SkillTree.learned.affordable() and \
                    len(self.Tribe.get_free_tribesmen()) == len(self.Tribe.population):
                self._blit_button(YES,YES)
            else:
                if len(self.Tribe.get_free_tribesmen()) < len(self.Tribe.population):
                    self._blit_text(self.Txt.get_txt('controls',1006))
                    #Whole tribe is required
                else:
                    self._blit_text(self.Txt.get_txt('controls',1005))
                    #insufficien resource
                self._next_line(self.HeaderText.get_height())
                self._blit_icon('grayed_yes')
            return None

        _command_handler()
        self._prepare_menu()
        self._blit_text(self.Txt.get_txt('controls', 1004)) #Available skills
        self._next_line(self.HeaderText.get_height())
        for skill in self.Tribe.SkillTree.available_skills:
            experience = skill.get_exp()
            self._blit_button('question','skill_info_' + _number_to_str(skill.id),
                              MENU_COLUMNS[-1][0])
            if experience == 'done':
                _blit_ready(skill)
                self._blit_icon(YES,MENU_COLUMNS[1][0])
            else:
                _blit_requirements(skill,experience)
            self._next_line()

        self._blit_delimiter()
        if self.Tribe.SkillTree.learned:
            _blit_selected(self.Tribe.SkillTree.learned)
            self._next_line()
            _yes_conditions()
        self._blit_button(NO,NO,MENU_COLUMNS[5][0])
        self._next_line()

        self._compleate_menu()

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

    def _blit_text(self, text, type = 'regular', offset = (0,0),
                   bold = False, coordinates = None):
        '''
        (self, str, (int, int), (int, int), bool) -> NoneType

        Blits text. If 'bold' passed as True than bold text will be blited.
        '''
        text = self.Txt.translator(text)

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

    def _blit_button(self, image, method, offset=0):
        '''
        (self, Surface, str, int) -> NoneType

        Blits button at current line with defined picture and offset in px
        to left. Creates instance of Button class and adds it in the buttons
        list.
        '''
        pic = self.Loader.get(BUTTON,image)
        draw_rect = pic.get_rect()
        draw_rect.top = self.menu_line[1]
        draw_rect.left = self.menu_line[0] + offset
        self.ScreenSurface.blit(pic, draw_rect)
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

        #draw_rect = self.Loader.controls[image].get_rect()
        draw_rect = self.Loader.get(ICON,image).get_rect()
        draw_rect.top = self.menu_line[1]
        draw_rect.left = self.menu_line[0] + offset
        #self.ScreenSurface.blit(self.Loader.controls[image],draw_rect)
        self.ScreenSurface.blit(self.Loader.get(ICON,image),draw_rect)

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
        self._blit_icon('point',SECOND_BUTTON_COLUMN)
        self._blit_text('x' + str(tribesman.points),'header',SECOND_TEXT_COLUMN)

        return None

    def _blit_equip(self, tribesman):
        '''
        (tribesman) -> None

        Blits tribesman weapon, armor, consumable item and its amount.
        '''
        if tribesman.weapon:
            image = 'item' + str(tribesman.weapon.id)
        else:
            image = 'unarmed'
        self._blit_icon(image,SECOND_BUTTON_COLUMN)
        if tribesman.wear:
            image = 'item' + str(tribesman.wear.id)
        else:
            image = 'undressed'

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
        def _create_party():
            '''
            (None) -> None

            Creates a party for all kinds of activities that requires
            tribesmen participation.
            '''
            self.menu_mode = 'party_builder'
            self.menu_submode = 'points'
            self.Party = party.Party(self.Tribe, self.selected.cell,
                                     self.called_method)
            self.free_list = self.Tribe.get_free_tribesmen()
            _print_parties()
            return None

        def _yes_handler():
            '''
            (None) -> None

            Handles all cases when pressed button is YES.
            '''
            def _yes_for_party():
                '''
                (None) -> None

                Clicking yes in party builder.
                If Party is valid - creation is finished.
                If there are no more available tribesmen - send parties.
                '''
                self.Tribe.parties.append(self.Party)
                print('Created party:', self.Party)
                self.party_list = []
                self.menu_mode = 'general'
                if len(self.Tribe.get_free_tribesmen()) == 0 and \
                        len(self.Tribe.send_query) == 0 and \
                        len(self.Tribe.parties) > 0:
                    self.Tribe.build_send_query()
                return None

            def _yes_for_popup():
                '''
                (None) -> None

                Clicking yes in popup menu.
                Clears screen from popup and disable pause.
                '''
                self.menu_mode = 'general'
                self.pause = False
                self.ScreenSurface.blit(self.Core.ClearLandscape,
                                        POPUP_RECT, POPUP_RECT)
                for x in range(1, 5):
                    for y in range(1,3):
                        self.Core.map[x][y].blit_markers(self.ScreenSurface)
                return None

            def _yes_for_skills():
                '''
                (None) -> None

                Clicking yes in popup menu.
                Passes Skill ID for Skill that mastered.
                '''
                Party = party.Party(self.Tribe, self.selected.cell,PROCESS_SKILL,
                                     self.Tribe.get_free_tribesmen())
                self.Tribe.parties.append(Party)
                self.Tribe.build_send_query()
                self.menu_mode = 'general'
                return None

            if self.menu_mode == 'party_builder' and\
                    not self.Party.is_valid(self.Tribe):
                _yes_for_party()
            elif self.menu_mode == 'popup':
                _yes_for_popup()
            elif self.menu_mode == SKILLS_MENU:
                _yes_for_skills()

            return None

        def _no_handler():
            '''
            (None) -> None

            Handles all cases when pressed button is NO.
            '''
            def _no_for_party():
                '''
                (None) -> None

                Clicking no for party builder menu.
                Deletes draft party instance.
                '''
                del self.Party
                self.party_list = []
                self.menu_mode = 'general'
                return None

            def _no_for_skills():
                '''
                (None) -> None

                Clicking no for skills menu.
                Deletes draft party instance.
                '''
                self.menu_mode = 'general'
                self.Tribe.SkillTree.learned = None
                return None

            if self.menu_mode == 'party_builder':
                _no_for_party()
            elif self.menu_mode == SKILLS_MENU:
                _no_for_skills()

            return None

        def _switch_submode():
            '''
            (None) -> None

            Changes submode for menus:
            - party builder
            '''
            def _sw_party_builder():
                '''
                (None) -> None

                Switches between submodes in party builder mode.
                '''
                if self.menu_submode == 'points':
                    self.menu_submode = 'equip'
                elif self.menu_submode == 'equip':
                    self.menu_submode = 'points'
                else:
                    assert False, 'Incorrect party builder submode initiated.'
                return None

            if self.menu_mode == 'party_builder':
                _sw_party_builder()

            return None

        def _skills_menu():
            '''
            (None) -> None

            Switches controls to display Skills menu.
            '''
            self.menu_mode = SKILLS_MENU

            return None

        def _print_parties():
            '''
            (None) -> None

            Prints defined parties in console
            '''
            print('Defined parties:')
            for defined_party in self.Tribe.parties:
                print('\t' + str(defined_party))
            return None

        if position[0] >= FIELD_WIDTH:
            for button in self.buttons:
                if button['rect'].collidepoint(position):
                    self.called_method = button['method']
                    self.update = True
                    if self.called_method in FORM_PARTY:
                        _create_party()
                    elif self.called_method == YES:
                        _yes_handler()
                    elif self.called_method == NO:
                        _no_handler()
                    elif self.called_method == SUBMODE:
                        _switch_submode()
                    elif self.called_method == SKILLS_MENU:
                        _skills_menu()

        else:
            if self.menu_mode == 'general':
                (x,y) = tools.pxToCellCoordinate(position)
                self.Core.set_selected_cell(self.selected.cell,(x,y))
                self.selected = self.Core.map[x][y]
                self.update = True
                print((x,y))

        return None
















