
#CONSTANTS
#Uplading constants from setup.ini file
from source import tools
import random
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
    """Helper class for Core that calculates results of any action
    according to game rules """

    def __init__(self, Core):
        '''
        (self, Core) -> None
        '''
        self.Core = Core

        self.resource_cost_matrix = {
            FIELD:   {'food':3, 'hunt':3, 'wood':0, 'stone':0},
            FOREST:  {'food':2, 'hunt':1, 'wood':4, 'stone':0},
            MOUNTAIN:{'food':3, 'hunt':3, 'wood':0, 'stone':6},
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
        self.Core.map[x][y].decrease_resource(resource, resource_amount)
        Party.loot = {resource:resource_amount}
        Party.output(str(resource_amount) + ' ' + resource + ' is collected.')

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
        richness = self.Core.map[x][y].richness(resource)
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
        cell_type = self.Core.map[x][y].land_type
        cost = self.resource_cost_matrix[cell_type][resource]

        return cost

    def tribe_activities(self, Party):
        '''
        (Party) -> None

        Precess food from to stocked food.
        '''
        if 'food' in Party.purpose:
            amount = self._calculate_total_points(Party)
            rest = Party.Tribe.consume_resource(FOOD,amount)
            Party.Tribe.add_resource(STOCKED_FOOD,amount-rest)
            Party.output(str(amount-rest) + ' food is stocked.')

        elif 'man' in Party.purpose:
            Tribe = Party.Tribe
            man = Party.members[0]
            woman=Party.members[1]
            if len(Tribe.population) < 15:
                if man.points == 5 and woman.points == 5:
                    name = 'Kid'
                    Tribe.add_tribesman(name)
                    Party.output(name + ' was born.')
                else:
                    Party.output('Population is not healthy enough to give a new life.')
            else:
                Party.output('Population limit is reached.')
        elif 'heal' in Party.purpose:
            for man in Party.members:
                man.heal()
            Party.output(str(len(Party.members))+ ' tribesmen were cured for 1 point each.')
        if 'skin' in Party.purpose:
            amount = self._calculate_total_points(Party) // 4
            rest = Party.Tribe.consume_resource(MOIST_SKIN,amount)
            Party.Tribe.add_resource(SKIN,amount-rest)
            Party.output(str(amount-rest) + ' peaces of skin are dressed.')

        return None

    def feeding(self,Tribe):
        '''
        (None) -> None

        Feeding tribesmen in the end of the day.
        If required food amount is not enough than tribesman suffers one point.
        If tribesmen point amount is 0 - he dies.
        '''
        feed = len(Tribe.population)
        Tribe.output(str(feed) + ' food is required for feeding.')
        feed = self.reduce_food(Tribe,feed)
        if feed == 0:
            return None
        Tribe.output('Available food was not enough and '+ str(feed) +
              ' stocked food is required.')
        feed = self.reduce_stocked_food(Tribe,feed)
        if feed == 0:
            return None
        Tribe.output('Stock is empty. Deficit is '+ str(feed) + ' food.')
        Tribe.print_points()
        self.population_damage(Tribe.population,feed)
        Tribe.print_points()
        Tribe.remove_dead()

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

    def population_damage(self,tribesmen_list,amount):
        '''
        (list of tribesmen, int) -> None

        Deals damage to list of tribesmen randomly. If amount is higher
        than number of tribesmen than deal damage to all and calls itself
        again with remained damage amount. When tribesmen points is 0 he dies.
        WARNING: No validation for losing conditions are performed.
        '''
        alive = 0
        total_points = 0
        for man in tribesmen_list:
            if man.is_alive():
                alive += 1
                total_points += man.points
        if alive == 0:
            return None
        if amount > total_points:
            amount = total_points
        if alive > amount:
            suffered = []
            while amount > 0:
                lucky =  random.randint(0,len(tribesmen_list)-1)
                if lucky in suffered:
                    continue
                else:
                    if tribesmen_list[lucky].is_alive():
                        tribesmen_list[lucky].suffer()
                        amount -= 1
                        suffered.append(lucky)
                    else:
                        suffered.append(lucky)
        else:
            amount -= alive
            for man in tribesmen_list:
                if man.is_alive():
                    man.suffer(1)
            self.population_damage(tribesmen_list,amount)

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

    def _log(self, line, console = True, log = True):
        '''
        (str, bool, bool) -> None

        Passes entry to log
        '''
        self.Core.Logger.append(line,console,log)

        return None



















