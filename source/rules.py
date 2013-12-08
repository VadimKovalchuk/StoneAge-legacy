
#CONSTANTS
#Uplading constants from setup.ini file
from source import tools
constants = tools.importConstants()
'''___________________________________________________________'''
#Land cell types
FIELD = constants['FIELD']      #Default is 'field'
FOREST = constants['FOREST']    #Default is 'forest'
MOUNTAIN = constants['MOUNTAIN']#Default is 'mountain'
WATER = constants['WATER']      #Default is 'water'
CAMP = constants['CAMP']        #Default is 'camp'
#Resource types
FOOD =          constants['FOOD']        #Default is 'food'
STOCKED_FOOD =  constants['STOCKED_FOOD']#Default is 'stocked_food'
HIDDEN_BONES =  constants['HIDDEN_BONES']#Default is 'hidden_bones'
BONES =         constants['BONES']       #Default is 'bones'
MOIST_SKIN =    constants['MOIST_SKIN']  #Default is 'moist_skin'
SKIN =          constants['SKIN']        #Default is 'skin'
WOOD =          constants['WOOD']        #Default is 'wood'
ROCK =          constants['STONE']        #Default is 'rock'
#Resource richness in land cell
EMPTY = constants['EMPTY']      #Default is 'empty'
LOW = constants['LOW']          #Default is 'low'
MODERATE = constants['MODERATE']#Default is 'moderate'
MANY = constants['MANY']        #Default is 'many'
RICH = constants['RICH']        #Default is 'rich'
del constants
'''___________________________________________________________'''

class Rules:
    """Helper class for Map that calculates results of any action
    according to game rules """

    def __init__(self, Map):
        '''
        (Map) -> NoneType
        '''
        self.Map = Map

        self.resource_cost_matrix = {
            FIELD:   {'food':3, 'hunt':3, 'wood':0, 'stone':0},
            FOREST:  {'food':2, 'hunt':1, 'wood':4, 'stone':0},
            MOUNTAIN:{'food':3, 'hunt':3, 'wood':0, 'stone':5},
            WATER:   {'food':0, 'hunt':1, 'wood':0, 'stone':0}
        }

        return None


    def resource_gathering(self,Party):
        '''
        (Party) -> None

        Calculates how many resources is collected by party.
        Depends of distance to home cell and land type (different land
        type has different cost for same resource.
        '''
        penalty = self.calculate_penalty(Party)
        points = self._calculate_total_points(Party,penalty)
        cost = self._get_cost(Party)
        assert cost,'Error during resource gathering calculation'
        resource_amount = points // cost


        (x, y) = Party.destination_cell
        resource = Party.purpose[4:]
        self.Map.map[x][y].decrease_resource(resource, resource_amount)
        Party.loot = {resource:resource_amount}

        print(Party.Tribe.name,resource_amount, resource)

        return None

    def calculate_penalty(self, Party):
        '''
        (Party) -> int

        Calculates penalty between home cell and destination cell.
        Penalty is 1 point per cell for tribesman if cell distance
        is more than 1.
        '''
        home_coords = Party.Tribe.home_cell.cell
        dest_coords = Party.destination_cell
        x_diff = abs(home_coords[0] - dest_coords[0])
        y_diff = abs(home_coords[1] - dest_coords[1])
        diff = max(x_diff,y_diff)
        result = diff - 1 + self._richness_penalty(Party)

        if result < 0:
            return 0
        else:
            return result

    def _richness_penalty(self, Party):
        '''
        ((int,int),str) -> int

        Calculates penalty for resource depending from its exhaustion
        at specified cell.
        '''
        (x, y) = Party.destination_cell
        resource = Party.purpose[4:]
        richness = self.Map.map[x][y].richness(resource)
        if richness == RICH:
            return 0
        elif richness == MANY:
            return 1
        elif richness == MODERATE:
            return 2
        elif richness == LOW:
            return 3
        elif richness == EMPTY:
            return 5
        else:
            assert False, 'Invalid resource richness parameter "'+ richness + '"'

    def _calculate_total_points(self,Party, penalty = 0):
        '''
        (Party, int) -> int

        Calculates how many points is spent on resource gathering.
        '''
        points = 0

        for man in Party.members:
            man_points = man.points - penalty
            if man_points < 0:
                man_points = 0
            points += man_points
        return points

    def _get_cost(self,Party):
        '''
        (Party) -> None

        Calculate cost for required resource from defined cell.
        '''
        (x, y) = Party.destination_cell
        resource = Party.purpose[4:]
        cell_type = self.Map.map[x][y].land_type
        cost = self.resource_cost_matrix[cell_type][resource]

        return cost

    def tribe_activities(self, Party):
        '''
        (Party) -> None

        Precess food from to stocked food.
        '''
        if 'food' in Party.purpose:
            amount = self._calculate_total_points(Party)
            rest = self.reduce_food(Party.Tribe,amount)
            Party.Tribe.add_resource(STOCKED_FOOD,amount-rest)

        return None

    def feeding(self,Tribe):
        '''
        (None) -> None

        Feeding tribesmen in the end of the day.
        If required food amount is not enough than tribesman suffers one point.
        If tribesmen point amount is 0 - he dies.
        '''
        feed = len(Tribe.population)
        feed = self.reduce_food(Tribe,feed)
        if feed == 0:
            return None
        feed = self.reduce_stocked_food(Tribe,feed)
        if feed == 0:
            return None
        self._starving_tribe(Tribe)

        return None

    def reduce_food(self,Tribe,amount):
        '''
        (Tribe, int) -> int

        Reduces tribes food list, transfers bones from hidden bones list to
        bones one. Than iterate over food list from last item to first one.
        If food list contains only zeros than return remained rest of
        required food.
        '''
        length = len(Tribe.resources[FOOD])
        food_list = Tribe.resources[FOOD]
        hidden_bones_list = Tribe.resources[HIDDEN_BONES]
        rest = amount

        for i in range(length-1,-1,-1):
            if food_list[i] == 0:
                continue
            elif rest > food_list[i]:
                reduced = food_list[i]
            else:
                reduced = rest
            rest -= reduced
            food_list[i] -= reduced

            if hidden_bones_list[i] == 0:
                pass
            elif reduced // 2 > hidden_bones_list[i]:
                Tribe.resources[BONES] += hidden_bones_list[i]
                hidden_bones_list[i] = 0
            else:
                hidden_bones_list[i] -= reduced // 2
                Tribe.resources[BONES] += reduced //2

            if rest ==0:
                return 0

        return rest

    def reduce_stocked_food(self, Tribe, amount):
        '''
        (Tribe, int) -> int

        Reduces tribes food list, transfers bones from hidden bones list to
        bones one. Than iterate over food list from last item to first one.
        If food list contains only zeros than return remained rest of
        required food.
        '''
        length = len(Tribe.resources[STOCKED_FOOD])
        food_list = Tribe.resources[STOCKED_FOOD]
        rest = amount

        for i in range(length-1,-1,-1):
            if food_list[i] == 0:
                continue
            elif rest > food_list[i]:
                reduced = food_list[i]
            else:
                reduced = rest
            rest -= reduced
            food_list[i] -= reduced
            if rest ==0:
                return 0

        return rest

        return 0

    def _starving_tribe(self,Tribe):
        pass

        return None

    def repository_maintenance(self,Tribe):
        '''
        (Tribe) -> None

        Shifts food and expiring date materials lists to one item up
        '''
        for res in (FOOD,HIDDEN_BONES,MOIST_SKIN,STOCKED_FOOD):
            for i in range(len(Tribe.resources[res])-1,0,-1):
                Tribe.resources[res][i] = Tribe.resources[res][i-1]
            Tribe.resources[res][0] = 0

        return None

















