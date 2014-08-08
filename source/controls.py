import pygame, sqlite3

#CONSTANTS
#Uplading constants from setup.ini file
from source import tools, party, items

constants = tools.Constants()
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
#Resource types
FOOD =          constants['FOOD']        #Default is 'food'
STOCKED_FOOD =  constants['STOCKED_FOOD']#Default is 'stocked_food'
BONE =         constants['BONE']       #Default is 'bone'
HIDDEN_BONE =  constants['HIDDEN_BONE']#Default is 'hidden_bone'
MOIST_SKIN =    constants['MOIST_SKIN']  #Default is 'moist_skin'
SKIN =          constants['SKIN']        #Default is 'skin'
WOOD =          constants['WOOD']        #Default is 'wood'
STONE =         constants['STONE']       #Default is 'stone'
#Dirrectories
DB_DIR = constants['DB_DIR']
del constants

OPEN_ALL = False
BUTTON_SIZE = 35
LINE_WIDTH = 2
FIRST_TEXT_COLUMN = (int(BUTTON_SIZE *1.1), BUTTON_SIZE // 3)
SECOND_BUTTON_COLUMN = int(BUTTON_SIZE *2.5)
SECOND_TEXT_COLUMN = (int(BUTTON_SIZE *3.6), BUTTON_SIZE // 3)
MENU_COLUMNS = [(0,BUTTON_SIZE // 3),
               (int(BUTTON_SIZE *1.1 - 1), BUTTON_SIZE // 3),
               (int(BUTTON_SIZE *2.2 - 2), BUTTON_SIZE // 3),
               (int(BUTTON_SIZE *3.3 - 3), BUTTON_SIZE // 3),
               (int(BUTTON_SIZE *4.4 - 4), BUTTON_SIZE // 3),
               (int(SIDE_PANEL_WIDTH - LINE_WIDTH * 8 - BUTTON_SIZE), BUTTON_SIZE // 3)]

#Buttons
SUBMODE = 'submode'
YES = 'yes'
NO = 'no'
PROCESS_MAN =  'process_man'
PROCESS_FOOD = 'process_food'
PROCESS_SKIN = 'process_skin'
PROCESS_HEAL = 'process_heal'
PROCESS_SKILL = 'process_skill'
PROCESS_WORKSHOP = 'process_workshop'
GET_FOOD = 'get_food'
GET_HUNT = 'get_hunt'
GET_WOOD = 'get_wood'
GET_STONE = 'get_stone'
SKILLS_MENU = 'skills_menu'
FORM_PARTY = [PROCESS_MAN, PROCESS_FOOD, PROCESS_SKIN,PROCESS_HEAL,
              PROCESS_WORKSHOP, GET_FOOD, GET_HUNT, GET_WOOD, GET_STONE]
RES_TO_ITEM = {FOOD: 42, STOCKED_FOOD: 43, MOIST_SKIN: 44,
                SKIN: 45, WOOD: 46, STONE: 47, BONE: 48}
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
        self.image = Image() #Picture aliases
        self.item_catalog_data = {'object':self.Tribe.Workshop,
                                  'item_dict':{},'revert_menu': 'general'}
        self.inventory_data = {'selected': None}
        #Internal variables
        self.HeaderText = pygame.font.SysFont(None, 24)
        self.RegularText = pygame.font.SysFont(None, 20)
        self.res_skill_depend = {'hunt':2, 'wood':1, 'stone':8}

        self.menu_line = [WINDOW_WIDTH - SIDE_PANEL_WIDTH +LINE_WIDTH * 4,
                          LINE_WIDTH * 4]
        self.block_topleft = [0,0]
        self.block_height = 0

        return None

    def refresh(self):
        '''
        (None) -> None
        '''
        if self.update or \
            self.Core.update or \
            self.Core.raise_popup or \
            self.Tribe != self.Core.active_tribe:
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
        elif self.menu_mode == 'workshop':
            self._blit_workshop_menu()
        elif self.menu_mode == 'item_catalog':
            self._blit_item_catalog()
        elif self.menu_mode == 'inventory':
            self._blit_inventory()
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
                if not OPEN_ALL:
                    if resource in self.res_skill_depend:
                        skill_id = self.res_skill_depend[resource]
                        if skill_id not in self.Tribe.SkillTree.active_skills:
                            continue

                # Blits button which creates the party for specific resource
                self._blit_button('cell_' + resource,'get_' + resource)

                # Blits resource richness
                richness = self.selected.richness(resource)
                self._blit_icon(richness,FIRST_TEXT_COLUMN[0])

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

        Blits tribe menu section. All buttons are blit according to skill
        dependencies of current tribe.
        '''
        def is_visible(skill_id):
            '''
            (int) -> bool

            Returns true if current tribe mastered skill by passed ID.
            '''
            if OPEN_ALL:
                return True
            else:
                return skill_id in self.Tribe.SkillTree.active_skills

        def heal_button():
            '''
            (None) -> bool

            Verifies if someone is injured.
            '''
            for man in self.Tribe.population:
                if man.points < 5:
                    return True

            return False

        def population_line():
            '''
            (None) -> None

            Blits population amount and buttons for increasing population,
            healing and inventory.
            '''
            self._blit_button('tribesman',PROCESS_MAN)
            self._blit_text('x ' + str(len(self.Tribe.population)),
                            'header', FIRST_TEXT_COLUMN)
            if heal_button():
                self._blit_button('heal',PROCESS_HEAL,SECOND_BUTTON_COLUMN)
            return True

        def food_line():
            '''
            (None) -> None

            Blits amount and buttons for stocked and raw food.
            '''
            self._blit_icon(FOOD)
            self._blit_text('x ' + str(self.Tribe.get_resource(FOOD)),
                            'header', FIRST_TEXT_COLUMN)
            if is_visible(3):#STOCKED_FOOD
                self._blit_button(STOCKED_FOOD,PROCESS_FOOD,
                                    offset=SECOND_BUTTON_COLUMN)
                self._blit_text('x ' + str(self.Tribe.get_resource(STOCKED_FOOD)),
                                'header', SECOND_TEXT_COLUMN)

            return True

        def bones_line():
            '''
            (None) -> None

            Blits bones amount and button for workshop.
            '''
            if is_visible(2): #Hunting
                self._blit_icon(BONE)
                self._blit_text('x ' + str(self.Tribe.get_resource(BONE)),
                                'header', FIRST_TEXT_COLUMN)
            else:
                return False

            return True

        def skin_line():
            '''
            (None) -> None

            Blits amount and buttons for raw and treated skin.
            '''
            if not is_visible(7):#Skin treating
                return False
            self._blit_icon(MOIST_SKIN)
            self._blit_text('x ' + str(self.Tribe.get_resource(MOIST_SKIN)),
                            'header', FIRST_TEXT_COLUMN)

            self._blit_button(SKIN,PROCESS_SKIN,
                                offset=SECOND_BUTTON_COLUMN)
            self._blit_text('x ' + str(self.Tribe.get_resource(SKIN)),
                            'header', SECOND_TEXT_COLUMN)
            return True

        def wood_line():
            '''
            (None) -> None

            Blits wood amount and camp fire(not implemented) indicator.
            '''
            if is_visible(1):#Wood
                self._blit_icon(WOOD)
                self._blit_text('x ' + str(self.Tribe.get_resource(WOOD)),
                                'header', FIRST_TEXT_COLUMN)
                if self.Tribe.resources['fire']:
                    self._blit_icon('fire', SECOND_BUTTON_COLUMN)
                else:
                    self._blit_icon('grayed_fire', SECOND_BUTTON_COLUMN)

                return True

        def stone_line():
            '''
            (None) -> None

            Blits stone amount and button for skills.
            '''
            if is_visible(8): #Stone
                self._blit_icon(STONE)
                self._blit_text('x ' + str(self.Tribe.get_resource(STONE)),
                                'header', FIRST_TEXT_COLUMN)
                return True

        def tribe_line():
            '''
            (None) -> None

            Blits tribe management buttons.
            '''
            self._blit_delimiter()
            self._blit_button('wheel',SKILLS_MENU,MENU_COLUMNS[0][0])
            know_items = len(self.Tribe.SkillTree.available_items)
            if know_items or OPEN_ALL:
                self._blit_button('workshop', 'workshop', MENU_COLUMNS[1][0])
            if self.Tribe.inventory or OPEN_ALL:
                self._blit_button('inventory', 'inventory', MENU_COLUMNS[2][0])
            self._blit_button('next', 'next', MENU_COLUMNS[-1][0])

            return True

        lines = (population_line, food_line, bones_line, skin_line,
                 wood_line, stone_line, tribe_line)
        self._prepare_menu()

        self._blit_text(self.Tribe.name, 'header')
        self._next_line(self.HeaderText.get_height())

        for line in lines:
            blited = line()
            if blited:
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

            Blits button for menu sub mode switching.
            '''
            if self.menu_submode == 'points':
                mode_image = 'hit_point'
            elif self.menu_submode == 'equip':
                mode_image = 'point'
            self._blit_button(mode_image, SUBMODE, FIRST_TEXT_COLUMN[0])

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

            Gets picture that should be blit for current popup.
            '''
            if 'picture' in self.popup_obj.popup:
                return self.image[self.popup_obj.popup['picture']]
            else:
                return self.popup_obj.popup['type'][0]

        self.pause = True
        self.ScreenSurface.blit(self.Loader.get('background', 'popup'),
                                POPUP_RECT)
        self.ScreenSurface.blit(self.Loader.get(POPUP,_popup_pic()), POPUP_PIC)
        popup_text = self.Txt.popup(self.popup_obj)
        _blit_popup_text(popup_text, 1)
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

        def _blit_requirements(skill, req):
            '''
            (Skill, dict) -> None

            Blits Skill as an icon and requirements for its study. Help button
            is also added for Skill.
            '''
            self._blit_icon('skill' + str(skill.id))
            self._blit_icon(req['resource'],
                            MENU_COLUMNS[1][0])
            txt = str(req['obtained']) + '/' + str(req['required'])
            self._blit_text(txt,'header',MENU_COLUMNS[2])


            return None

        def _blit_ready(skill):
            '''
            (Skill) -> None

            Blits Skill as a button when required experience is gained.
            '''
            self._blit_button('skill' + str(skill.id),
                              'skill' + _number_to_str(skill.id))
            return None

        def _blit_selected(skill):
            '''
            (Skill) -> None

            Blits selected Skill separately as an icon and its price.
            '''
            self._blit_icon('skill' + str(skill.id))
            price = skill.get_price()
            for resource in price:
                if type(resource) == type(''):
                    self._blit_icon(resource, MENU_COLUMNS[1][0])
                else:
                    self._blit_icon('item' + str(resource), MENU_COLUMNS[1][0])
                available = self.Tribe.get_ingredient_amount(resource)
                required = price[resource]
                text = 'x' + str(available) + '/' + str(required)
                self._blit_text(text,'header', MENU_COLUMNS[2])
                if available >= required:
                    self._blit_icon(YES, MENU_COLUMNS[-1][0])
                else:
                    self._blit_icon('grayed_yes',MENU_COLUMNS[-1][0])
                self._next_line()

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
                    self._blit_text(self.Txt.get_txt('controls',1006)) #Whole tribe is required
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
            _yes_conditions()
        self._blit_button(NO,NO,MENU_COLUMNS[5][0])
        self._next_line()

        self._compleate_menu()

        return None

    def _blit_workshop_menu(self):
        '''
        (None) -> None

        Blits Workshop Menu.
        '''
        def id_to_item():
            '''
            (None) -> None

            If item in selected slot is just ID than creates Item object with
            this ID.
            '''
            if self.Tribe.Workshop.selected and \
                type(self.Tribe.Workshop.selected) == type(1):
                    self.Tribe.Workshop.selected = \
                        items.Item(self.Tribe.Workshop.selected)

            return None

        def blit_selected():
            '''
            (None) -> None

            Blits item icon that selected for crafting.
            '''
            self._next_line(BUTTON_SIZE // 2)
            if self.Tribe.Workshop.selected:
                item = self.Tribe.Workshop.selected
                pic = 'item' + str(item.id)
            else:
                pic = 'goods'
            if self.Tribe.Workshop.production:
                self._blit_icon(pic,MENU_COLUMNS[1][0] // 2)
            else:
                self._blit_button(pic,'item_catalog',MENU_COLUMNS[1][0] // 2)
            #blits extra frame
            indent = LINE_WIDTH*2
            self._blit_frame(self.menu_line[0]-indent + MENU_COLUMNS[1][0] // 2,
                             self.menu_line[1]- indent,
                             BUTTON_SIZE + indent * 2,
                             BUTTON_SIZE + indent * 2)
            return None

        def blit_points():
            '''
            (None) -> None

            Blits amount of points that requires or remains for selected
            item crafting.
            '''
            if not self.Tribe.Workshop.selected:
                return None
            item = self.Tribe.Workshop.selected
            self._blit_icon('point',MENU_COLUMNS[2][0])
            if self.Tribe.Workshop.production:
                text = 'x' + str(self.Tribe.Workshop.points) + \
                       '/' + str(item.ingredients['point'])
            else:
                text = 'x' + str(item.ingredients['point'])
            self._blit_text(text,'header',MENU_COLUMNS[3])

            return None

        def blit_ingredients():
            '''
            (dict) -> None

            Blits ingredients for item in Workshop 'selected' slot
            '''
            if self.Tribe.Workshop.selected:
                ingredients = self.Tribe.Workshop.selected.ingredients
                for ingredient in ingredients:
                    if ingredient == 'point':
                        continue
                    if type(ingredient) == type(1):
                        icon = 'item' + str(ingredient)
                    else:
                        icon = ingredient
                    self._blit_icon(icon,MENU_COLUMNS[0][0])
                    required = ingredients[ingredient]
                    available =self.Tribe.get_ingredient_amount(ingredient)
                    text = 'x' + str(available) + ' / ' + str(required)
                    self._blit_text(text, 'header', MENU_COLUMNS[1])
                    if available >= required:
                        self._blit_icon(YES, MENU_COLUMNS[3][0])
                    else:
                        self._blit_icon('grayed_yes',MENU_COLUMNS[3][0])
                    self._next_line()
            else:
                self._blit_text(self.Txt.get_txt('controls',1007),offset=(MENU_COLUMNS[0][0],-6)) #Select item
                #self._next_line()

            return None

        def blit_tribesmen():
            '''
            (None) -> None

            If party is build for Workshop blits tribesman icon and amount
            of participants. Else blits button which evokes party builder.
            '''
            for party in self.Tribe.parties:
                if party.purpose == PROCESS_WORKSHOP:
                    self._blit_icon('tribesman')
                    amount = str(len(party.members))
                    self._blit_text('x' + amount,'header',MENU_COLUMNS[1])
                    return None
            else:
                self._blit_button('tribesman', PROCESS_WORKSHOP)
            return None

        def blit_yes_no():
            '''
            (None) -> None

            When item is not selected or Tribe has no required amount
            of ingredients - grayed out yes icon is blited. If all
            conditions are satisfied  - YES button is blited. When Workshop
            is in production state - cancel button is blited.
            '''
            position = MENU_COLUMNS[3][0]
            if self.Tribe.Workshop.production:
                self._blit_button(NO,NO,position)
            elif self.Tribe.Workshop.selected and self.Tribe.Workshop.conditions():
                self._blit_button(YES, YES, position)
            else:
                self._blit_icon('grayed_yes',position)

            return None

        #method body
        id_to_item()
        self._prepare_menu()
        blit_selected()
        blit_points()
        self._next_line()
        self._blit_delimiter()
        if not self.Tribe.Workshop.production:
            blit_ingredients()
        self._blit_delimiter()
        blit_tribesmen()
        blit_yes_no()
        self._blit_button('next',NO,MENU_COLUMNS[-1][0])
        self._next_line()

        self._compleate_menu()

        return None

    def _blit_item_catalog(self):
        '''
        (None) -> None

        Blits Item Catalog for item selection.
        '''
        def command_handler():
            '''
            (None) -> None

            When item button is pressed - assigns its id to selected
            attribute of issued object
            '''
            if 'category' in self.called_method:
                self.menu_submode = self.called_method[9:]
            elif 'selected' in self.called_method:
                id = self.called_method[9:]
                self.item_catalog_data['object'].selected = int(id)
            elif 'info' in self.called_method:
                item_id = int(self.called_method[10:])
                self.Core.popup = {'type':['item_info'],
                                   'item':item_id,
                                   'picture':'item' + str(item_id)}
                self.Core.raise_popup = True

            return None

        def is_one_category():
            '''
            (None) -> None

            If item_dict have only one category, proceeds directly to it
            '''
            item_dict = self.item_catalog_data['item_dict']
            if len(item_dict) == 1:
                category = list(item_dict.keys())
                self.menu_submode = category[0]

            return None

        def blit_item_info(id):
            '''
            (int) -> None

            Blits item data according to its type.
            '''
            def blit_damage_range(column):
                '''
                (int) -> None

                Blits item damage range starting from passed column.
                '''
                min = str(item.points[0])
                max = str(item.points[-1])
                text = ' '.join((min, '-',max))
                self._blit_icon('hit_point',MENU_COLUMNS[column][0])
                self._blit_text(text,'header',MENU_COLUMNS[column + 1])
                return None

            def blit_amount():
                '''
                (None) -> None

                Blits amount and of item.
                '''
                amount = str(item.amount)
                text = ''.join((' x',amount))
                self._blit_text(text,'header',MENU_COLUMNS[1])
                return None

            def weapon():
                blit_damage_range(1)
                return  None

            def armor():
                '''
                (None) -> None

                Blits item amount of armor
                '''
                armor = str(item.points[0])
                text = ''.join(('x',armor))
                self._blit_icon('hit_point',MENU_COLUMNS[1][0])
                self._blit_text(text,'header',MENU_COLUMNS[2])
                return None

            def ammo():
                blit_amount()
                blit_damage_range(2)
                return None

            def consumable():
                blit_amount()
                return None

            blit_type = {'weapon':weapon, 'range':weapon, 'armor':armor,
                         'ammo':ammo, 'consumable':consumable}
            item = items.Item(id)
            blit_type[item.type]()

            return None

        def blit_categories():
            '''
            (None) -> None

            Blits available categories in item dictionary
            '''
            for category in self.item_catalog_data['item_dict']:
                self._blit_button(category,'category_' + category)
                self._next_line()
            return None

        def blit_subcategory():
            '''
            (None) -> None

            Blits subcategory that defined in menu_submode attribute of controls
            '''
            for item_id in self.item_catalog_data['item_dict'][self.menu_submode]:
                self._blit_button('item' + str(item_id),'selected_' + str(item_id))
                blit_item_info(item_id)
                self._blit_button('question','info_item_' + str(item_id),
                                  MENU_COLUMNS[-1][0])
                self._next_line()
            return None

        def blit_selected():
            '''
            (None) -> None

            Blits selected object and its data separately
            '''
            if self.item_catalog_data['object'].selected:
                selected = self.item_catalog_data['object'].selected
                if type(selected) == type(1):
                    id = selected
                else:
                    id = selected.id
                self._blit_icon('item' + str(id))
                blit_item_info(id)
                self._next_line()
            return None

        def blit_yes():
            '''
            (None) -> None

            If item is selected - blits active button. Otherwise - grayed out
            '''
            if self.item_catalog_data['object'].selected:
                self._blit_button(YES, YES)
            else:
                self._blit_icon('grayed_yes')

        command_handler()
        is_one_category()
        self._prepare_menu()
        if self.menu_submode == 'general':
            blit_categories()
        else:
            blit_subcategory()
        self._blit_delimiter()
        blit_selected()
        blit_yes()
        self._blit_button(NO, NO, MENU_COLUMNS[-1][0])
        self._next_line()
        self._compleate_menu()

        return None

    def _blit_inventory(self):
        '''
        (None) -> None

        Blits inventory for passing items between tribe and tribesmen.
        '''
        def command_handler():
            '''
            (None) -> None

            Handles changes that should be done by button presses.
            '''
            def item_to_res(item):
                    '''
                    (item) -> str
                    '''
                    if item:
                        for res in RES_TO_ITEM:
                            if RES_TO_ITEM[res] == item.id:
                                return res
                    return None

            def tribesman():
                '''
                (None) -> None

                Changes inventory menu submode when tribesman is selected
                '''
                index = int(self.called_method[-3:])
                self.inventory_data['selected'] = self.free_list[index]
                self.menu_submode = 'pass'

                return None

            def remove_item():
                '''
                (None) -> None

                Removes specified item from selected tribesman inventory.
                '''
                if 'weapon' in self.called_method:
                    weapon = self.inventory_data['selected'].weapon
                    self.Tribe.add_items(weapon)
                    self.inventory_data['selected'].weapon = None
                elif 'wear' in self.called_method:
                    wear = self.inventory_data['selected'].wear
                    self.Tribe.add_items(wear)
                    self.inventory_data['selected'].wear = None
                elif 'item' in self.called_method:
                    index = int(self.called_method[-1])
                    item = self.inventory_data['selected'].inventory[index]
                    res = item_to_res(item)
                    if res:
                        self.Tribe.add_resource(res, 1)
                    else:
                        self.Tribe.add_items(item)
                    self.inventory_data['selected'].inventory[index] = None
                return None

            def equip():
                '''
                (None) -> None

                Equips with selected item. If slot is already equipped - switches items.
                '''
                def man_inventory(item):
                    '''
                    (None) -> None

                    Equips consumable item. If consumable list is full -
                    returns last to inventory.
                    '''
                    inventory = self.inventory_data['selected'].inventory
                    res = item_to_res(inventory[2])
                    if res:
                        self.Tribe.add_resource(res, 1)
                    else:
                        self.Tribe.add_items(inventory[2])
                    inventory[2] = inventory[1]
                    inventory[1] = inventory[0]
                    inventory[0] = item

                    return None

                def pass_resource():
                    '''
                    (None) -> None

                    If resource is selected for passing to inventory - creates corresponding
                    item and passes it to tribesman inventory.
                    '''
                    for res in RES_TO_ITEM:
                        if res in self.called_method:
                            if res == FOOD and STOCKED_FOOD in self.called_method:
                                continue
                            self.Tribe.consume_resource(res, 1)
                            man_inventory(items.Item(RES_TO_ITEM[res]))
                            return None

                if 'res' in self.called_method:
                    pass_resource()
                    return None
                uniq, cons = split_items()
                index = int(self.called_method[-3:])
                if  index < 500:
                    item = uniq.pop(index)
                    self.Tribe.inventory.remove(item)
                    item = self.inventory_data['selected'].add_item(item)
                    self.Tribe.add_items(item)
                else:
                    item = cons.pop(index - 500)
                    if item.amount > 5:
                        item.amount -= 5
                        man_inventory(items.Item(item.id))
                    else:
                        self.Tribe.inventory.remove(item)
                        man_inventory(item)
                return None

            if 'tribesman' in self.called_method:
                tribesman()
            elif 'remove' in self.called_method:
                remove_item()
            elif 'pass' in self.called_method:
                equip()

            return None

        def split_items():
            '''
            (None) -> list, list

            Split tribe inventory list on two lists. One with consumable
            items and other with unique.
            '''
            unique_lst = []
            consumable_lst = []
            for item in self.Tribe.inventory:
                if item.type == 'consumable' or item.type == 'ammo':
                    consumable_lst.append(item)
                else:
                    unique_lst.append(item)
            return unique_lst, consumable_lst

        def blit_tribesmen():
            '''
            (None) -> None

            Blits free tribesmen list
            '''
            counter = 0
            for tribesman in self.free_list:
                self._blit_button('tribesman', 'tribesman' + tools.number_to_str(counter))
                self._blit_text(tribesman.name, 'header',MENU_COLUMNS[1])
                self._blit_equip(tribesman)
                counter += 1
                self._next_line()
            return None

        def blit_selected():
            '''
            (None) -> None

            Blits free tribesmen list
            '''
            tribesman = self.inventory_data['selected']
            self._blit_icon('tribesman')
            self._blit_text(tribesman.name, 'header',MENU_COLUMNS[1])
            self._next_line()
            # Blits weapon button
            if tribesman.weapon:
                weapon = ''.join(('item', str(tribesman.weapon.id)))
                self._blit_button(weapon,'remove_weapon')
            else:
                self._blit_icon('unarmed')
            # Blits wear button
            if tribesman.wear:
                wear = ''.join(('item', str(tribesman.wear.id)))
                self._blit_button(wear,'remove_wear',MENU_COLUMNS[1][0])
            else:
                self._blit_icon('unarmed',MENU_COLUMNS[1][0])

            #Blits items buttons
            for index,item in enumerate(tribesman.inventory):
                if item:
                    item_pic = ''.join(('item', str(item.id)))
                    self._blit_button(item_pic,'remove_item'+ str(index),
                                      MENU_COLUMNS[index + 2][0])
                else:
                    self._blit_icon('goods',MENU_COLUMNS[index + 2][0])
                #counter += 1
            self._next_line()
            self._blit_delimiter()
            blit_tribe_inventory()
            #self._next_line()

            return None

        def blit_tribe_inventory():
            '''
            (None) -> None

            Blits tribe inventory under selected tribesman.
            '''
            def blit_unique_items(items):
                '''
                (list of Items) -> None

                Blits list of unique items.
                '''
                for i,item in enumerate(items):
                    offset = MENU_COLUMNS[1][0] * (i % 5)
                    #print(offset, str(item))
                    item_pic = ''.join(('item', str(item.id)))
                    index = tools.number_to_str(i)
                    self._blit_button(item_pic, 'pass_' + index, offset)
                    if i%5 == 4 and i != (len(items) - 1):
                        self._next_line()
                return None

            def blit_consumable_items(items):
                '''
                (list of items) -> None

                Blits list of consumable items.
                '''
                for i,item in enumerate(items):
                    if i%2:
                        button_offset = SECOND_BUTTON_COLUMN
                        text_offset = SECOND_TEXT_COLUMN
                    else:
                        button_offset = 0
                        text_offset = FIRST_TEXT_COLUMN
                    item_pic = ''.join(('item', str(item.id)))
                    index = tools.number_to_str(i + 500)
                    self._blit_button(item_pic, 'pass_' + index, button_offset)
                    text = ''.join((' x', str(item.amount)))
                    self._blit_text(text, 'header',text_offset)
                    if i%2 or i == (len(items) - 1):
                        self._next_line()

                return None

            def blit_resources():
                '''
                (None) -> None

                Blits Tribes available resources.
                '''
                resources = [FOOD, STOCKED_FOOD, BONE, MOIST_SKIN, SKIN, WOOD, STONE]
                for res in resources[:]:
                    if not self.Tribe.get_resource(res):
                        resources.remove(res)
                amount = len(resources) - 1
                for i, res in enumerate(resources):
                    offset = MENU_COLUMNS[1][0] * (i % 5)
                    self._blit_button(res,'pass_res_' + res,offset)
                    if i%5 ==4 or i == amount:
                        self._next_line()
                return None


            if not self.Tribe.inventory:
                return None
            unique_lst, consumable_lst = split_items()
            blit_unique_items(unique_lst)
            self._next_line()
            self._blit_delimiter()
            blit_consumable_items(consumable_lst)
            blit_resources()
            self._blit_delimiter()

            return None

        submodes = {'tribesmen':blit_tribesmen, 'pass':blit_selected}
        command_handler()
        self._prepare_menu()
        submodes[self.menu_submode]()
        self._blit_button( 'next' ,NO , MENU_COLUMNS[-1][0])
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

    def _blit_text(self, text, type = 'regular', offset = (0, 0),
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
            text_line = self.HeaderText.render(str(text), True, (0, 0, 0))
        elif type == 'regular':
            text_line = self.RegularText.render(str(text), True, (0, 0, 0))
        text_rect = text_line.get_rect()

        if not coordinates:
            coordinates = self.menu_line
        text_rect.left = coordinates[0] + offset[0]
        text_rect.top = coordinates[1] + offset[1]

        self.ScreenSurface.blit(text_line, text_rect)

        if bold:
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
        image = self.image[image]
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
        image = self.image[image]
        draw_rect = self.Loader.get(ICON,image).get_rect()
        draw_rect.top = self.menu_line[1]
        draw_rect.left = self.menu_line[0] + offset
        self.ScreenSurface.blit(self.Loader.get(ICON, image), draw_rect)

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
        def create_party():
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
            print_parties()
            return None

        def yes_handler():
            '''
            (None) -> None

            Handles all cases when pressed button is YES.
            '''
            def yes_for_party():
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

            def yes_for_popup():
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

            def yes_for_skills():
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

            def yes_for_workshop():
                '''
                (None) -> None

                Starts item crafting process.
                '''
                self.Tribe.Workshop.start_crafting()
                return None

            def yes_for_item_catalog():
                '''
                (None) -> None

                Reverts to menu that evokes Item Catalog with id that pass to
                corresponding object 'selected parameter'.
                '''
                self.menu_mode = self.item_catalog_data['revert_menu']

                return None

            if self.menu_mode == 'party_builder' and\
                    not self.Party.is_valid(self.Tribe):
                yes_for_party()
            elif self.menu_mode == 'popup':
                yes_for_popup()
            elif self.menu_mode == SKILLS_MENU:
                yes_for_skills()
            elif self.menu_mode == 'item_catalog':
                yes_for_item_catalog()
            elif self.menu_mode == 'workshop':
                yes_for_workshop()

            return None

        def no_handler():
            '''
            (None) -> None

            Handles all cases when pressed button is NO.
            '''
            def no_for_party():
                '''
                (None) -> None

                Clicking NO in party builder menu.
                Deletes draft party instance.
                '''
                del self.Party
                self.party_list = []
                self.menu_mode = 'general'
                return None

            def no_for_skills():
                '''
                (None) -> None

                Clicking NO in skills menu.
                Deletes draft party instance.
                '''
                self.menu_mode = 'general'
                self.Tribe.SkillTree.learned = None
                return None

            def no_for_workshop():
                '''
                (None) -> None

                Clicking NO in workshop menu.
                Cancels item creation.
                '''
                self.menu_mode = 'general'
                return None

            def no_for_item_catalog():
                '''
                (None) -> None

                Reverts to menu that evokes Item Catalog with clearing
                id that pass to corresponding object 'selected' parameter.
                '''
                self.item_catalog_data['object'].selected = None
                self.menu_mode = self.item_catalog_data['revert_menu']

                return None

            def no_for_inventory():
                '''
                (None) -> None

                Reverts to tribesmen menu from passed man submenu and
                exits from tribesmen menu to general.
                '''
                if self.menu_submode == 'pass':
                    self.menu_submode = 'tribesmen'
                elif self.menu_submode == 'tribesmen':
                    self.menu_mode = 'general'

                return None

            if self.menu_mode == 'party_builder':
                no_for_party()
            elif self.menu_mode == SKILLS_MENU:
                no_for_skills()
            elif self.menu_mode == 'workshop':
                no_for_workshop()
            elif self.menu_mode == 'item_catalog':
                no_for_item_catalog()
            elif self.menu_mode == 'inventory':
                no_for_inventory()

            return None

        def switch_submode():
            '''
            (None) -> None

            Changes submode for menus:
            - party builder
            '''
            def sw_party_builder():
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
                sw_party_builder()

            return None

        def skills_menu():
            '''
            (None) -> None

            Switches controls to display Skills menu.
            '''
            self.menu_mode = SKILLS_MENU

            return None

        def next_turn():
            '''
            (None) -> None

            Assigns free tribesmen into idle party and overs the turn.
            '''
            self.menu_mode = 'party_builder'
            self.Party = party.Party(self.Tribe, self.Tribe.home_cell.cell, 'idle')
            self.free_list = self.Tribe.get_free_tribesmen()
            self.Party.members = self.free_list[:]
            yes_handler()

            return None

        def workshop():
            '''
            (None) -> None

            Switch controls to workshop menu display mode.
            '''
            self.menu_mode = 'workshop'

            return None

        def item_catalog():
            '''
            (None) -> None

            Switch controls to Item Catalog menu display mode with validation
            of item_catalog_data dictionary content
            '''
            def workshop():
                '''

                '''
                if OPEN_ALL:
                    item_dict = tools.all_items_catalog()
                else:
                    item_dict = self.Tribe.SkillTree.available_items
                self.item_catalog_data = {'object': self.Tribe.Workshop,
                                  'item_dict':item_dict,
                                  'revert_menu': 'workshop'}
                self.menu_submode = 'general'
                return None

            if self.menu_mode == 'workshop':
                workshop()
            self.menu_mode = 'item_catalog'
            self.menu_submode = 'general'

            return None

        def inventory():
            '''
            (None) -> None

            Switches controls to display Inventory menu.
            '''
            self.menu_mode = 'inventory'
            self.free_list = self.Tribe.get_free_tribesmen()
            self.menu_submode = 'tribesmen'

            return None

        def print_parties():
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
                        create_party()
                    elif self.called_method == YES:
                        yes_handler()
                    elif self.called_method == NO:
                        no_handler()
                    elif self.called_method == SUBMODE:
                        switch_submode()
                    elif self.called_method == SKILLS_MENU:
                        skills_menu()
                    elif self.called_method == 'next':
                        next_turn()
                    elif self.called_method == 'workshop':
                        workshop()
                    elif self.called_method == 'item_catalog':
                        item_catalog()
                    elif self.called_method == 'inventory':
                        inventory()
        else:
            if self.menu_mode == 'general':
                (x,y) = tools.pxToCellCoordinate(position)
                self.Core.set_selected_cell(self.selected.cell,(x,y))
                self.selected = self.Core.map[x][y]
                self.update = True
                print((x,y))

        return None


class Image:
    """Class for getting aliases to images from DB """

    def __init__(self):
        '''
        Creates cursor to DB
        '''
        db = sqlite3.connect(DB_DIR + 'core.db')
        self.db_cursor = db.cursor()
        self.aliases = {}

        return None

    def __getitem__(self, alias):
        '''
        Gets alias to picture name.
        If entry with such name is not found then returns alias to
        error picture.
        '''
        if alias in self.aliases:
            return self.aliases[alias]
        self.db_cursor.execute('SELECT picture FROM pic_aliases WHERE alias = "'+\
                               str(alias)+'"')
        value = self.db_cursor.fetchone()
        if value:
            self.aliases[alias] = value[0]
            return value[0]
        else:
            print('Alias "' + alias + '" is NOT found.')
            return ''













