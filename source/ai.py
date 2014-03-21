from source import tools, party

#CONSTANTS
#Uplading constants from setup.ini file
constants = tools.Constants()
'''___________________________________________________________'''
#Number of cells by X and Y axises
LAND_NUM_Y      = constants['LAND_NUM_Y']       #Default 4
LAND_NUM_X      = constants['LAND_NUM_X']       #Default 6
#Land cell types
FIELD = constants['FIELD']      #Default is 'field'
FOREST = constants['FOREST']    #Default is 'forest'
MOUNTAIN = constants['MOUNTAIN']#Default is 'mountain'
WATER = constants['WATER']      #Default is 'water'
CAMP = constants['CAMP']        #Default is 'camp'
del constants
'''___________________________________________________________'''

class Ai:
    """ Tribe helper class that performs decisions in case if tribe
     is not player"""

    def __init__(self, Tribe):
        '''
        (Tribe) -> NoneType

        '''
        self.Tribe = Tribe
        self.priority_res = {
            'food':        1,
            'stocked_food':2,
            'bones':       3,
            'moist_skin':  4,
            'skin':        5,
            'wood':        6,
            'rock':        7}
        self.coord_list = []

        self.gen_coord_list()

        return None

    def generate_parties(self):
        '''
        (None) -> None
        '''
        for cell_coord in self.coord_list:
            (x,y) = cell_coord
            if self.Tribe.Core.map[x][y].get_resource('food') > 0:
                free_list = self.Tribe.get_free_tribesmen()
                if len(free_list) == 0:
                    break
                elif len(free_list) >= 5:
                    prt = party.Party(self.Tribe, cell_coord,'get_food')
                    for i in range(0,5):
                        prt.add_member(free_list[i])
                    self.Tribe.parties.append(prt)
                elif len(free_list) < 5:
                    prt = party.Party(self.Tribe, self.selected.cell,'get_food')
                    for i in range(0,len(free_list)):
                        prt.add_member(free_list[i])
                    self.Tribe.parties.append(prt)
        print('Move by',self.Tribe.name,'is done:')
        for group in self.Tribe.parties:
            print(group)
        self.Tribe.build_send_query()

        return None

    def _is_valid_coord(self, coordinate):
        '''
        ((int, int)) ->bool

        Verifies if passed coordinate is valid.
        '''
        (x,y) = coordinate
        if x in range(0,LAND_NUM_X) and \
            y in range(0,LAND_NUM_Y)and \
            self.Tribe.home_cell.cell != coordinate:
            return True
        else:
            return False

    def gen_coord_list(self):
        ''''''
        coordinate = self.Tribe.home_cell.cell
        for x in range(-1,2):
            for y in range(-1,2):
                iterable_coord = (coordinate[0] + x, coordinate[1] + y)
                if self._is_valid_coord(iterable_coord):
                    self.coord_list.append(iterable_coord)
        #print(self.coord_list)
        return None