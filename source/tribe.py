import pygame
from source import tribesman
from source import ai

#CONSTANTS
#Uplading constants from setup.ini file
from source import tools
constants = tools.importConstants()
'''___________________________________________________________'''
#Timing and delay intervals
SEND_INTERVAL = constants['SEND_INTERVAL']        #Default is 'food'
#Resource types
FOOD =          constants['FOOD']        #Default is 'food'
STOCKED_FOOD =  constants['STOCKED_FOOD']#Default is 'stocked_food'
BONES =         constants['BONES']       #Default is 'bones'
HIDDEN_BONES =  constants['HIDDEN_BONES']#Default is 'hidden_bones'
MOIST_SKIN =    constants['MOIST_SKIN']  #Default is 'moist_skin'
SKIN =          constants['SKIN']        #Default is 'skin'
WOOD =          constants['WOOD']        #Default is 'wood'
STONE =         constants['STONE']      #Default is 'stone'
del constants
'''___________________________________________________________'''

class Tribe:
    """ Tribe class """

    def __init__(self, name, Loader, Map, LandCell,  player = 'CPU'):
        '''
        (land_cell, str, (int, int), str, str, custom) -> NoneType

        Contains all information about tribesman:
        - name
        - land cell coordinates (x, y);
        - absolute coordinates
        - (!not implemented) tribesman rectangle
        - owned instrument/weapon;
        - weared costume/armor;
        - inventory (dictionary where key is a item and value is its number)
        - custom attribute for quests purposes
        '''

        self.name = name
        self.Map = Map
        self.home_cell = LandCell
        self.population = []
        self.parties = []
        self.send_query = []
        self.ready = False
        self.query_timer = pygame.time.get_ticks()
        self.meeple_sprite = Loader.sprites['player_walk']
        self.player_type = player
        self.AI = ai.Ai(self)
        self.resources = {
            FOOD:        [0,0,0],
            STOCKED_FOOD:[0,0,0,0,0,0],
            HIDDEN_BONES:[0,0,0],
            BONES:       0,
            MOIST_SKIN:  [0,0,0],
            SKIN:        0,
            WOOD:        0,
            STONE:       0
        }

        return None
        

    def add_tribesman(self, name, instrument = None, wear = None, custom = None):
        '''
        (str, str, str, dict) -> Tribesman

        Adds new tribesman to tribe population with the passed
        parameters and returns reference to added one.
        '''
        new_member = tribesman.Tribesman(self.meeple_sprite, name,\
                                         self.home_cell.cell,\
                                         instrument,wear,custom)
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
        if self.player_type == 'player':
            return None
        else:
            self.AI.generate_parties()

        return None

    def day(self):
        '''
        (None) - > None

        Performs processing that should be done in the day phase.
        '''
        if self.ready == True:
            return None

        for group in self.parties:
            if 'get' in group.purpose:
                self.Map.Rules.resource_gathering(group)
            elif 'process' in group.purpose:
                pass
            elif 'quest' in group.purpose:
                #Not implemented
                pass
            else:
                assert False, 'incorrect party command syntax'+ str(self.purpose)
        self.ready = True

        return None

    def everning(self):
        '''
        (None) - > None

        Performs processing that should be done in the everning phase.
        '''
        if self.ready == True:
            return None
        self._loot_transfer()
        self._feeding()
        self._repository_maintanance()

        self.ready = True

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
            else:
                assert False, 'Incorrect party command syntax'+ str(self.purpose)

        return None

    def _feeding(self):
        '''
        (None) -> None

        Feeding tribesmen in the end of the day.
        If required food amount is not enough than tribesman suffers one point.
        If tribesmen point amount is 0 - he dies.
        '''
        length = len(self.resources[FOOD])
        assert length == len(self.resources[HIDDEN_BONES]), \
            'Incorrect BONES list length - ' + \
            str(len(self.resources[HIDDEN_BONES]))
        assert length == len(self.resources[MOIST_SKIN]), \
            'Incorrect BONES list length - ' + \
            str(len(self.resources[MOIST_SKIN]))

        return None

    def _repository_maintanance(self):
        '''
        (None) -> None

        Shifts food and expiring date materials lists to one item up
        '''
        pass

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
                waypoint = self.Map.PathFinder.get_path(start, end)
                party_member.travel(waypoint)

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
                self.Map.active_sprites.append(self.send_query[0])
                self.send_query.pop(0)
                return None

            if self._all_reached():
                    print('All tribesmen from',self.name,'has reached their locations.')
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

    def add_resource(self, type, amount):
        '''
        (str, int) -> None

        Adds passed number to specified resource
        '''
        if type in (STOCKED_FOOD,FOOD,MOIST_SKIN,HIDDEN_BONES):
            self.resources[type][0] += amount
        elif type == 'hunt':
            self.resources[FOOD][0] += amount
            self.resources[HIDDEN_BONES][0] += amount // 2
            self.resources[MOIST_SKIN][0] += amount // 4
        else:
            self.resources[type] += amount
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














