import pygame
from source import tribesman
from source import ai
from source import skilltree

#CONSTANTS
#Uplading constants from setup.ini file
from source import tools
constants = tools.Constants()
'''___________________________________________________________'''
#Loader image categories
SPRITE        = constants['SPRITE']
#Timing and delay intervals
SEND_INTERVAL = constants['SEND_INTERVAL']        #Default is 700
#Resource types
FOOD =          constants['FOOD']        #Default is 'food'
STOCKED_FOOD =  constants['STOCKED_FOOD']#Default is 'stocked_food'
BONE =         constants['BONE']         #Default is 'bone'
HIDDEN_BONE =  constants['HIDDEN_BONE']  #Default is 'hidden_bone'
MOIST_SKIN =    constants['MOIST_SKIN']  #Default is 'moist_skin'
SKIN =          constants['SKIN']        #Default is 'skin'
WOOD =          constants['WOOD']        #Default is 'wood'
STONE =         constants['STONE']      #Default is 'stone'
del constants
'''___________________________________________________________'''

class Tribe:
    """ Tribe class """

    def __init__(self, name, Loader, Core, LandCell,  player = 'CPU'):
        '''
        (str, Loader, Core, LandCell, str) -> NoneType

        Contains all information about tribe:
        - name
        - Loader reference
        - Core reference
        - home land cell reference
        - tribe type
        '''

        self.name = name
        self.Core = Core
        self.home_cell = LandCell
        self.population = []
        self.inventory = []
        self.statistics = {}
        self.parties = []
        self.send_query = []
        self.ready = False
        self.popup = {}
        self.raise_popup = False
        self.query_timer = pygame.time.get_ticks()
        self.meeple_sprite = Loader.get(SPRITE,'player_walk')
        self.player_type = player
        self.AI = ai.Ai(self)
        self.SkillTree = skilltree.SkillTree(self)
        self.Workshop = Workshop(self)
        self.resources = {
            FOOD:        [0,0,0],
            STOCKED_FOOD:[0,0,0,0,0,0,0,0,0],
            HIDDEN_BONE:[0,0,0],
            BONE:       0,
            MOIST_SKIN:  [0,0,0],
            SKIN:        0,
            WOOD:        0,
            STONE:       0,
            'fire':      0
        }

        return None
        

    def add_tribesman(self, name, instrument = None, wear = None, custom = None):
        '''
        (str, str, str, dict) -> Tribesman

        Adds new tribesman to tribe population with the passed
        parameters and returns reference to added one.
        '''
        new_member = tribesman.Tribesman(self.meeple_sprite, name,\
                                         self.home_cell.cell)
        self.population.append(new_member)

        return new_member

    def get_free_tribesmen(self):
        '''
        (None) -> list
        '''
        if len(self.parties) == 0:
            return self.population[:]
        else:
            result_list = self.population[:]
            for party in self.parties:
                for party_member in party.members:
                    result_list.remove(party_member)
            return result_list

    def morning(self):
        '''
        (None) -> None

        Performs activities required in the morning phase.
        '''
        if self.ready:
            return None
        if not self.player_type == 'player':
            self.AI.generate_parties()

        return None

    def day(self):
        '''
        (None) - > None

        Performs processing that should be done in the day phase.
        '''
        if self.ready == True:
            return None
        self._log(self.name + ':')
        for group in self.parties:
            if 'get' in group.purpose:
                self.Core.Rules.resource_gathering(group)
            elif 'process' in group.purpose:
                self.Core.Rules.tribe_activities(group)
            elif 'quest' in group.purpose:
                #Not implemented
                pass
            elif 'idle' in group.purpose:
                pass
            else:
                assert False, 'incorrect party command syntax'+ str(self.purpose)
        self.ready = True
        self._finalize_popup('daily')
        return None

    def everning(self):
        '''
        (None) - > None

        Performs processing that should be done in the everning phase.
        '''
        if self.ready == True:
            return None
        self._log(self.name + ':')
        self._loot_transfer()
        self.Core.Rules.feeding(self)
        self.Core.Rules.repository_maintenance(self)
        self.Core.Rules.treat_fire(self)
        self.parties = []
        self.ready = True
        self._finalize_popup('nightly')
        return None

    def _loot_transfer(self):
        '''
        (None) -> None

        Transferring gathered resources from parties to tribe repository
        '''
        for group in self.parties:
            if 'get' in group.purpose:
                for key in group.loot:
                    self.add_resource(key,group.loot[key])
            elif 'process' in group.purpose:
                pass
            elif 'quest' in group.purpose:
                #Not implemented
                pass
            elif 'idle' in group.purpose:
                pass
            else:
                assert False, 'Incorrect party command syntax'+ str(self.purpose)

        return None

    def build_send_query(self, home = False):
        '''
        (None) -> None

        Builds tribesmen sending query. Those that goes further are first(Not implemented).
        '''
        if len(self.parties) == 0:
            self.ready = True
            return None
        self.send_query = []
        for group in self.parties:
            for party_member in group.members:
                self.send_query.append(party_member)
                if home:
                    start = group.destination_cell
                    end = self.home_cell.cell
                else:
                    start = self.home_cell.cell
                    end = group.destination_cell
                waypoint = self.Core.PathFinder.get_path(start, end)
                party_member.travel(waypoint)
        #Fisrt should be send tribesmen that have to pass longer distance
        for n in range(0,len(self.send_query)-1):
            for i in range(0,len(self.send_query)-1):
                if len(self.send_query[i].m_waypoints) < \
                        len(self.send_query[i+1].m_waypoints):
                    self.send_query[i],self.send_query[i+1] = \
                        self.send_query[i+1],self.send_query[i]
        self.ready = True

        return None

    def send_parties(self):
        '''
        (None) -> None

        Initiates adding tribesmen to map animation conveyor.
        '''
        if self.ready:
            return None
        time = pygame.time.get_ticks()
        if time - self.query_timer > SEND_INTERVAL:
            self.query_timer = time
            if len(self.send_query) > 0:
                self.Core.active_sprites.append(self.send_query[0])
                self.send_query.pop(0)
                return None

            if self._all_reached():
                    self._log('All tribesmen from '+ self.name +
                              ' has reached their locations.')
                    self.ready = True
        return None

    def _all_reached(self):
        '''
        (None) -> bool

        Checks if all tribesmen in tribe has reached destination location
        '''
        for group in self.parties:
            for meeple in group.members:
                if meeple.visible:
                    return False
        return True

    def get_resource(self,type):
        '''
        (str) -> int

        Returns available resource amount.
        '''
        result = 0
        if type in (STOCKED_FOOD,FOOD,MOIST_SKIN):
            for item in self.resources[type]:
                result += item
        else:
            result = self.resources[type]

        return result

    def get_item_amount(self, item):
        '''
        (int or Item) -> int

        Receives Item reference or item ID and returns its amount in
        Tribe inventory. Note that items that equipped on tribesmen
        are not count.
        '''
        if type(item) == type(1):
            id = item
        else:
            id = item.id
        amount = 0
        for item in self.inventory:
            if item.id == id:
                amount += item.amount
        return amount

    def get_ingredient_amount(self, ingredient):
        '''
        (str or int) -> int

        Gets ingredient amount from tribe.
        '''
        if type(ingredient) == type(''):
            amount = self.get_resource(ingredient)
        elif type(ingredient) == type(1):
            amount = self.get_item_amount(ingredient)
        else:
            assert False, 'Incorrect resource type is requested from tribe'

        return amount

    def add_resource(self, type, amount):
        '''
        (str, int) -> None

        Adds passed number to specified resource
        '''
        if type in (STOCKED_FOOD,FOOD,MOIST_SKIN,HIDDEN_BONE):
            self.resources[type][0] += amount
            self.add_statistics(type, amount)
        elif type == 'hunt':
            self.add_statistics('hunt', amount)
            self.resources[FOOD][0] += amount
            self.add_statistics(FOOD, amount)
            self.resources[HIDDEN_BONE][0] += amount // 2
            self.resources[MOIST_SKIN][0] += amount // 4
            self.add_statistics(MOIST_SKIN, amount // 4)
        else:
            self.resources[type] += amount
            self.add_statistics(type, amount)
        return None

    def add_items(self, items):
        '''
        (Item or list or tuple) -> None

        Adds item or items to tribe inventory. Consumable items and ammo
        are stacking.
        '''
        def add_stack(item):
            '''
            (Item) -> None

            Adds stackable item to tribe inventory. If this type already
            in inventory - just increases its amount.
            '''
            in_inventory = self.get_item_amount(item)
            if in_inventory:
                inventory_item = self.find_item(item.id)
                inventory_item.amount += item.amount
            else:
                self.inventory.append(item)
            return None

        def add_item(item):
            '''
            (Item) -> None

            Adds item to inventory. Stackable items are counted as single with
            increased amount value.
            '''
            if not item:
                return None
            if item.type in ('consumable', 'ammo'):
                add_stack(item)
            else:
                self.inventory.append(item)
            return None

        if type(items) in (type([]), type(())):
            for item in items:
                add_item(item)
        else:
            add_item(items)
        return None

    def add_statistics(self, stat_parameter, amount):
        '''
        (str, int) -> None

        Adds amount to statistics parameter. If statistics parameter is
        new - adds it.
        '''
        if stat_parameter in self.statistics:
            self.statistics[stat_parameter] += amount
        else:
            self.statistics[stat_parameter] = amount

        return None

    def consume_resource(self, type, amount):
        '''
        (str, int) -> None

        Adds passed number to specified resource
        '''
        rest = amount
        if type in (STOCKED_FOOD,FOOD,MOIST_SKIN,HIDDEN_BONE):
            consumable = self.resources[type]
            for i in range(len(consumable)-1,-1,-1):
                if consumable[i] == 0:
                    continue
                elif rest > consumable[i]:
                    reduced = consumable[i]
                else:
                    reduced = rest
                rest -= reduced
                consumable[i] -= reduced
        else:
            if amount <= self.resources[type]:
                self.resources[type] -= amount
                rest = 0
            else:
                rest -= self.resources[type]
                self.resources[type] = 0
        return rest

    def find_item(self, id):
        '''
        (int) -> Item

        Searches for item with passed id and returns its reference.
        Only first item with such id can be returned.
        '''
        if not len(self.inventory):
            return None
        for item in self.inventory:
            if item.id == id:
                return item
        return None

    def remove_items(self, item_id, amount = 1):
        '''
        (int, int) -> None

        Removes from inventory items with passed id with quantity that passed.
        '''
        for i in range(0,amount):
            item = self.find_item(item_id)
            if item.type in ('ammo', 'consumable'):
                item.amount -= 1
                if item.amount == 0:
                    self.inventory.remove(item)
            else:
                self.inventory.remove(item)

        return None

    def remove_dead(self):
        '''
        (None) -> None

        Removes dead tribesmen from the population list.
        !!Inventory retrieving from the corpse is not implemented.
        '''
        for man in self.population[:]:
            if not man.is_alive():
                self.population.remove(man)
                self.add_to_popup('dead', man.name)
                self._log(man.name + ' has died.')

        return None

    def print_points(self):
        '''
        (None) -> None

        Print out population points.
        '''
        total = 0
        log_str = '['
        for man in self.population:
            log_str += str(man.points) + ','
            total += man.points
        log_str += '] = '+ str(total)
        self._log(log_str)

        return None

    def _log(self, line, console = True, log = True):
        '''
        (str, bool, bool) -> None

        Passes entry to log
        '''
        self.Core.Logger.append(line,console,log)

        return None

    def add_to_popup(self, category, message):
        '''
        (str, str) -> None

        Appends message to passed category. If category is not exist - creates it.
        '''
        if category not in self.popup:
            self.popup[category] =[]
        self.popup[category].append(message)

        return None

    def _finalize_popup(self, type = None):
        '''
        (str) -> None

        Adds mandatory information into popup dictionary and raises flag
        for popup display.
        '''
        if self.player_type == 'player':
            if self.popup:
                if 'type' not in self.popup:
                    self.add_to_popup('type', type)
                self.raise_popup = True
        else:
            self.popup = {}
        return None

    def __str__(self):
        '''

        '''
        result = "\nTribe:" + self.name + "\n" 
        if len(self.population) == 0:
            return 'Tribe is empty'
        
        for meple in self.population:
            result = result + str(meple)

        return result

class Workshop:
    """ Support class for Tribe """

    def __init__(self, Tribe):
        '''
        (Tribe) -> NoneType

        Contains all information related to item production:
        - Tribe
        - current produced item
        - requirements
        - manpower counters
        '''

        self.Tribe = Tribe
        self.selected = None
        self.production = False
        self.points = 0

        return None

    def conditions(self):
        '''
        (None) -> bool

        Verifies if all ingredients are available for item production.
        '''
        assert self.selected.ingredients, 'Item is not selected in Workshop.'
        for ingredient in self.selected.ingredients:
            if ingredient == 'point':
                continue
            if type(ingredient) == type(1):
                available = self.Tribe.get_item_amount(ingredient)
            elif type(ingredient) == type(''):
                available = self.Tribe.get_resource(ingredient)
            else:
                assert False, 'Incorrect resource type is requested from tribe'
            required = self.selected.ingredients[ingredient]
            if required > available:
                return False

        return True

    def reset(self):
        '''
        (None) -> None

        Resets Workshop crafting parameters.
        '''
        self.production = False
        self.points = 0
        self.selected = None

        return None

    def process(self, points):
        '''
        (int) -> str

        Spend passed points amount into crafting process. If item is crafted
        put it into tribes inventory and returns True.
        Otherwise False is returned.
        '''
        def update_statistics(item = None):
            '''
            (Item) -> None

            Updates Tribes statistics with respect to new item type.
            '''
            item_type = self.selected.type
            if 'goods' not in self.Tribe.statistics:
                self.Tribe.statistics['goods'] = 0
            self.Tribe.statistics['goods'] += 1
            if item_type not in self.Tribe.statistics:
                self.Tribe.statistics[item_type] = 0
            self.Tribe.statistics[item_type] += 1
            return None

        if not (self.production or self.selected):
            return False
        self.points += points
        required = self.selected.ingredients['point']
        if self.points >= required:
            self.Tribe.add_items(self.selected)
            update_statistics(self.selected)
            self.reset()
            return True
        else:
            return False

    def start_crafting(self):
        '''
        (None) -> None

        Reduces amount of ingredients in Tribe and starts crafting process.
        '''
        assert self.conditions(), 'Incorrect crafting parameters'

        for ingredient in self.selected.ingredients:
            if ingredient == 'point':
                continue
            amount = self.selected.ingredients[ingredient]
            if type(ingredient) == type(''):
                self.Tribe.consume_resource(ingredient, amount)
            else:
                self.Tribe.remove_items(ingredient, amount)
        self.production = True
        return None









