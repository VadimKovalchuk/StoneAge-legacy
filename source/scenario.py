from source import tools

#CONSTANTS
#Uplading constants from setup.ini file
constants = tools.Constants()
'''___________________________________________________________'''
#Game directories
SCENARIO_DIR = constants['SCENARIO_DIR'] #Default is'scenario\\'
#Land cell types
FIELD = constants['FIELD']      #Default is 'field'
FOREST = constants['FOREST']    #Default is 'forest'
MOUNTAIN = constants['MOUNTAIN']#Default is 'mountain'
WATER = constants['WATER']      #Default is 'water'
CAMP = constants['CAMP']        #Default is 'camp'
del constants
'''___________________________________________________________'''

class Scenario:
    """ Scenario class defines landscape and daily events, organize
    interaction between storyline and gaming process"""

    def __init__(self, scenario_file):
        '''
        (str) -> NoneType

        '''

        self.files = {}
        self.map_line = []
        self.scripted_events = []
        self.daily_events = []
        self.random_events = []
        self.custom = {}

        # Geting map and list of files that contains events for
        # compleate scenario
        file = open(SCENARIO_DIR + scenario_file, 'r')
        for line in file:
            assert '=' in line, \
                   'Incorrect scenario file sintax("=" charecter is missing)'
            [key, value] = line.split('=')
            self.files[key] = value
        file.close()
        
        # Parcing map file and building 2D matrix in which each element is a
        # dictionary of cell parameters:
        '''
        - cell_index - absolute cell index. scripted events points on this index
        - land_type - type of the land cell. Valid values: grass, forest, rock,
                      water, camp
        - preset - reference to one of standard sets of resources volume and
                   random evente chance. Valid values: default, big?, small?,???
                   If none of defined is not sutable, than custom argument can be
                   used and all numbers and chances specified manualy.
        '''
        assert 'MAP' in self.files, \
               'MAP reference is not found in scenario: '+ scenario_file
        file = open(SCENARIO_DIR + self.files['MAP'], 'r')

        cell_index = 1
        splited_cell = []
        cell_data = {}
        cell_line = []

        for line in file:
            assert ' ' in line,\
                'Incorrect map file sintax(mandatory space charecter is missing)'
            cell_data['cell_index'] = cell_index
            splited_cell.extend(line.split())
            
            for pair in splited_cell:
                assert  '=' in pair,\
                'Incorrect map file sintax(mandatory "=" charecter is missing)'
                (name, value) = pair.split('=')
                cell_data[name] = value

            assert 'land_type' in cell_data,\
                'Incorrect map file format(parameter "land_type" is missing)'

            assert cell_data['land_type'] in (FIELD, FOREST, MOUNTAIN,\
                                              WATER, CAMP),\
                'Incorrect land type found( "'+cell_data['land_type']+'")'

            assert 'preset' in cell_data,\
                'Incorrect map file format(parameter "preset" is missing)'
            
            cell_line.append(cell_data)
                
            if cell_index % 4 == 0:
                self.map_line.append(cell_line)
                cell_line = []

            cell_data = {}
            splited_cell = []
            cell_index += 1
            
        #for x in self.map_line:
        #    for y in x:
        #        print(y)
        file.close()










     
        
        
