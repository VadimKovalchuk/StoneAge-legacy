

PROCESS_MAN =  'process_man'
PROCESS_FOOD = 'process_food'
PROCESS_SKIN = 'process_skin'
GET_FOOD = 'get_food'
GET_HUNT = 'get_hunt'
GET_WOOD = 'get_wood'
GET_STONE = 'get_stone'

class Party:
    """ Class for group of tribesmen that leaving camp for some activity """

    def __init__(self, Tribe, destination_cell, purpose, members = []):
        '''
        (Tribe,(int, int), str, list) -> NoneType

        Contains all information about sending party:
        - tribe that it belongs to
        - destination land cell coordinates (x, y)
        - purpose/reason why party has been send there
        - list of members that participate party
        - custom attributes that copied from custom attributes of all
          tribesmen in party

        Command syntax for party activity (self.purpose variable):
        "get_[resource]" - interaction with cells that out of camp for
                        gathering resources or quest activities(not implemented)
        "process_[resource]" - interaction within the tribe
        '''

        self.destination_cell = destination_cell
        self.Tribe = Tribe
        self.purpose = purpose
        self.members = members[:]
        self.limits = {}
        self.custom = {}
        self.loot = {}

        self._calculate_limits()

        return None

    def add_member(self, Tribesman):
        '''
        (Tribesman) -> None

        Adds tribesman to party
        '''
        self.members.append(Tribesman)

        return None

    def _calculate_limits(self):
        '''
        (None) -> None

        Defines value for self.limits - how many tribesmen can participate party
        '''
        if 'get' in self.purpose:
            self.limits = {'min': 1, 'max': 5}
        elif 'process' in self.purpose:
            self.destination_cell = self.Tribe.home_cell.cell
            if 'food' in self.purpose:
                self.limits = {'min': 1, 'max': 1}
            elif 'skin' in self.purpose:
                self.limits = {'min': 1, 'max': 1}
            elif 'man' in self.purpose:
                self.limits = {'min': 2, 'max': 2}
            elif 'workshop'in self.purpose:
                self.limits = {'min': 1, 'max': 1}
            elif 'heal' in self.purpose:
                self.limits = {'min': 1, 'max': 15}
            elif 'skill':
                pass
            else: assert False, 'Incorrect party command for tribe functionality'
        elif 'idle' in self.purpose:
            self.limits = {'min': 1, 'max': len(self.Tribe.population)}
        else: assert False, 'Incorrect party command type'

        return None

    def is_valid(self, Tribe):
        '''
        (None) -> None

        Analyze if created party is valid. Tribe parameters are used
        in check as well(tribe is taken from fist tribesman in member list.
        Performs following checks:
            - tribesmen number fits the limits
            - only 1 party of each type is allowed
        '''
        if self.limits['min'] > len(self.members):
            return 1001         #'Select participants'
        if len(self.members) > self.limits['max']:
            return 1002         #'To many participants'
        for Party in Tribe.parties:
            if Party.purpose == self.purpose:
                return 1003     #'only 1 activity allowed'

        return None

    def interact(self):
        '''
        (None) -> None

        Interact with cell or resource from tribe inventory.
        '''
        if 'get' in self.purpose:
            resource = self.purpose[4:]

        elif 'process' in self.purpose:
            resource = self.purpose[8:]
            
        elif 'quest' in self.purpose:
            #Not implemented
            pass

        else:
            assert False, 'incorrect party command syntax'+ str(self.purpose)


        return None

    def __str__(self):
        '''
        Returns following information about the party:
        destination cell coordinates, reason and how many members it has
        '''
        result = str(self.destination_cell) + ', ' + self.purpose +\
                 ', ' + str(len(self.members))

        return result

    def __del__(self):
        '''
        Clears members list
        '''
        for tribesman in self.members[:]:
            self.members.remove(tribesman)

        return None
