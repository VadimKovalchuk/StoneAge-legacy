
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
BONES =         constants['BONES']       #Default is 'bones'
MOIST_SKIN =    constants['MOIST_SKIN']  #Default is 'moist_skin'
SKIN =          constants['SKIN']        #Default is 'skin'
WOOD =          constants['WOOD']        #Default is 'wood'
ROCK =          constants['ROCK']        #Default is 'rock'
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
        self.cost_matrix = {
            FIELD:{}
            FOREST:{}
            MOUNTAIN:{}
            WATER:{}
        }

        return None


    def resource_gathering(self,Party):
        '''
        (Party) -> None

        Calculates how many resources is collected by party.
        Depends of distance to home cell and land type (different land
        type has different cost for same resource.
        '''
        home_coords = Party.Tribe.home_cell.cell
        dest_coords = Party.destination_cell.cell
        penalty = self.calculate_penalty(home_coords,dest_coords)


        return None

    def calculate_penalty(self, home_coords, dest_coords):
        '''
        ((int,int),(int,int)) -> int

        Calculates penalty between home cell and destination cell.
        Penalty is 1 point per cell for tribesman if cell distance
        is more than 1.
        '''
        x_diff = abs(home_coords[0] - dest_coords[0])
        y_diff = abs(home_coords[1] - dest_coords[1])
        diff = max(x_diff,y_diff)
        result = diff - 1
        if result < 0:
            return 0
        else:
            return result