
#CONSTANTS
#Uplading constants from setup.ini file
from source import tools
import random
constants = tools.Constants()
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
HIDDEN_BONE =  constants['HIDDEN_BONE']  #Default is 'hidden_bone'
BONE =         constants['BONE']         #Default is 'bones'
MOIST_SKIN =    constants['MOIST_SKIN']  #Default is 'moist_skin'
SKIN =          constants['SKIN']        #Default is 'skin'
WOOD =          constants['WOOD']        #Default is 'wood'
ROCK =          constants['STONE']       #Default is 'rock'
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

        line = ' '.join([str(resource_amount),resource])
        Party.Tribe.add_to_popup(2001, line) #Collected
        self._log('Collected: ' + line)

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
        resource = Party.purpose[4:]
        for man in Party.members:
            if resource == 'hunt':
                amount = man.hit()
            else:
                amount = man.points
            man_points = amount - penalty
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
            stocked = amount-rest
            Party.Tribe.add_resource(STOCKED_FOOD, stocked)
            Party.Tribe.add_to_popup(4001, stocked) # food are stocked
            self._log(str(stocked) + ' food are stocked.')
        elif 'man' in Party.purpose:
            Tribe = Party.Tribe
            man = Party.members[0]
            woman=Party.members[1]
            if len(Tribe.population) < 15:
                if man.points == 5 and woman.points == 5:
                    name = 'Kid'
                    Tribe.add_tribesman(name)
                    Party.Tribe.add_to_popup(4002, name) # was born
                    self._log(name + ' was born.')
                else:
                    Party.Tribe.add_to_popup(3001, '') #Population is not healthy enough to give a new life
                    self._log('Population is not healthy enough to give a new life.')
            else:
                Party.Tribe.add_to_popup(3002, '') #Population limit is reached
                self._log('Population limit is reached.')
        elif 'heal' in Party.purpose:
            for man in Party.members:
                man.heal()
                Party.Tribe.add_to_popup(4003, man.name) # got rest and healed
            self._log(str(len(Party.members))+ ' tribesmen were cured for 1 point each.')
        elif 'skin' in Party.purpose:
            amount = self._calculate_total_points(Party) // 4
            rest = Party.Tribe.consume_resource(MOIST_SKIN,amount)
            result = amount-rest
            Party.Tribe.add_resource(SKIN, result)
            Party.Tribe.add_to_popup(4004, result) # peaces of skin are dressed
            self._log(str(result) + ' peaces of skin are dressed.')
        elif 'skill' in Party.purpose:
            skill = Party.Tribe.SkillTree.learned
            price = skill.get_price()
            for resource in price:
                if type(resource) == type(''):
                    Party.Tribe.consume_resource(resource,price[resource])
                else:
                    Party.Tribe.remove_items(resource,price[resource])
            Party.Tribe.SkillTree.master_skill()
            Party.Tribe.popup = {'type':['skill_done'],'skill':skill.id,
                                       'picture':'skill' + str(skill.id)}
            self._log('Skill #' + str(skill.id) + ' is mastered.')
            Party.Tribe.SkillTree.learned = None
        elif 'workshop' in Party.purpose:
            amount = self._calculate_total_points(Party)
            name = Party.Tribe.Workshop.selected.get_name()
            Party.Tribe.add_to_popup(4007, amount) # peaces of skin are dressed
            self._log(str(amount) + ' points are spent for ' + name + ' creation.')
            created = Party.Tribe.Workshop.process(amount)
            if created:
                self._log('New item is created.')
                Party.Tribe.add_to_popup(4008, name) # peaces of skin are dressed

        return None

    def feeding(self,Tribe):
        '''
        (None) -> None

        Feeding tribesmen in the end of the day.
        If required food amount is not enough than tribesman suffers one point.
        If tribesmen point amount is 0 - he dies.
        '''
        feed = len(Tribe.population)
        Tribe.add_to_popup(4005, feed)  # food are required for feeding
        self._log(str(feed) + ' food are required for feeding.')
        feed = self.reduce_food(Tribe,feed)
        if feed == 0:
            return None

        Tribe.add_to_popup(3003, feed) #Available food amount is not enough
        Tribe.add_to_popup(4006, feed) # stocked food are required
        self._log('Available food was not enough and '+ str(feed) +
                    ' stocked food are required.')
        feed = self.reduce_stocked_food(Tribe,feed)

        if feed == 0:
            return None
        Tribe.add_to_popup(3004, feed) #Food stock is empty and your people suffer from hunger
        self._log('Stock is empty. Deficit is '+ str(feed) + ' food.')
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
        hidden_bones_list = Tribe.resources[HIDDEN_BONE]
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
                Tribe.resources[BONE] += hidden_bones_list[i]
                Tribe.add_statistics(BONE,hidden_bones_list[i])
                hidden_bones_list[i] = 0
            else:
                hidden_bones_list[i] -= reduced // 2
                Tribe.resources[BONE] += reduced //2
                Tribe.add_statistics(BONE,reduced //2)

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
        for res in (FOOD,HIDDEN_BONE,MOIST_SKIN,STOCKED_FOOD):
            for i in range(len(Tribe.resources[res])-1,0,-1):
                Tribe.resources[res][i] = Tribe.resources[res][i-1]
            Tribe.resources[res][0] = 0

        return None

    def treat_fire(self, Tribe):
        '''
        (Tribe) -> None

        Consumes one wood each two days to keep the fire.
        '''
        if Tribe.resources['fire']:
            Tribe.resources['fire'] -= 1
        if (not Tribe.resources['fire']) and Tribe.resources[WOOD]:
            Tribe.resources[WOOD] -= 1
            if self.Core.game_phase == 4:
                Tribe.resources['fire'] = 3
            else:
                Tribe.resources['fire'] = 4
        return None

    def skill_dependencies(self, Tribe, skill_id):
        '''
        (int) -> None

        Change tribe parameters according to newly learned skill.
        '''
        def skin_treating():
            '''
            (None) -> None

            When Skin treating is learned moist skin amount should be cleared.
            '''
            numbers = Tribe.resources[MOIST_SKIN]
            Tribe.resources[MOIST_SKIN] = [0 for i in numbers]

            return None

        def bones():
            '''
            (None) -> None

            When Hunting  is learned bones amount should be cleared.
            '''
            Tribe.resources[BONE] = 0

            return None

        skill_mapping = {7:skin_treating, 2:bones}
        if skill_id in skill_mapping:
            skill_mapping[skill_id]()

        return None

    def _log(self, line, console = True, log = True):
        '''
        (str, bool, bool) -> None

        Passes entry to log
        '''
        self.Core.Logger.append(line,console,log)

        return None





















