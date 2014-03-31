import glob, time, shutil, sqlite3

#Set up window resolution
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
#Number of cells by X and Y axises
LAND_NUM_Y = 4
LAND_NUM_X = 6
#Side(control) panel and game field width
SIDE_PANEL_WIDTH = WINDOW_WIDTH - WINDOW_HEIGHT // LAND_NUM_Y * LAND_NUM_X
FIELD_WIDTH = WINDOW_WIDTH - SIDE_PANEL_WIDTH
#Cell width and height
LAND_CELL_HEIGHT = WINDOW_HEIGHT // LAND_NUM_Y
LAND_CELL_WIDTH = LAND_CELL_HEIGHT

DB_DIR = 'database\\'
LOG_DIR = 'log\\'

def parse_func_name(func_ref):
    '''
    (func) -> str

    Returns function name by its reference.
    '''
    name = str(func_ref)
    index = name.find(' ')
    name = name[index + 1:]
    index = name.find(' ')
    name = name[:index]
    return name

class Constants:
    """Class for getting constants from DB """

    def __init__(self):
        '''
        Creates cursor to DB
        '''
        db = sqlite3.connect(DB_DIR + 'core.db') #DB_DIR +
        self.db_cursor = db.cursor()
        self.calc_func = ()
        self.calc_names = ()
        self.calculate(None)
        self.setup = self.parse_setup()

        return None

    def __getitem__(self, name):
        '''
        Tries to get constant value.
        If entry with such name is not found then evokes 'calculate'
        method and returns value that it generates.
        '''
        self.db_cursor.execute('SELECT value FROM constants WHERE name = "'+\
                               str(name)+'"')
        value = self.db_cursor.fetchone()
        if not value:
            if name in self.setup:
                value = self.setup[name]
            else:
                value = self.calculate(name)
        else:
            value = value[0]

        if type(value) == type(''):
            if value.isnumeric():
                value = int(value)
            else:
                value = self.tuple_builder(value)
        #print('Constant ' + name + ' is loaded with value - ' + str(value))
        return value

    def tuple_builder(self, value):
        '''
        (str) -> tuple

        Creates tuple from string if string is starts and ends with '(' and ')'
        '''
        if value[0] == '(' and value[-1] == ')':
            tuple_builder = value[1:-1].split(', ')
            for element in range(0,len(tuple_builder)):
                if tuple_builder[element].isnumeric():
                    tuple_builder[element] = int(tuple_builder[element])
            return tuple(tuple_builder)
        else:
            return value

    def parse_setup(self):
        '''
        (None) -> dict

        Imports all constants from setup.ini file and returns them as a dictionary where
        key is a constant name and value is a constant value
        '''
        constants = {}
        setup=open('setup.ini', 'r')
        for line in setup:
            if '=' in line:
                name,value = line.split('=')
                value = value[:-1]
                # If value is a number
                if value.isnumeric():
                    value = int(value)
                constants[name] = value
        setup.close()
        return constants

    def calculate(self,name):
        '''
        Verify if constant with such name exists in calculated constants
        list, calculates it and returns. Else asserts an error.
        '''
        def side_panel_width():
            #SIDE_PANEL_WIDTH = WINDOW_WIDTH - WINDOW_HEIGHT // LAND_NUM_Y * LAND_NUM_X
            width = self['WINDOW_WIDTH']
            height = self['WINDOW_HEIGHT']
            y = self['LAND_NUM_Y']
            x = self['LAND_NUM_X']
            return width - height // y * x

        def field_width():
            #FIELD_WIDTH = WINDOW_WIDTH - SIDE_PANEL_WIDTH
            return self['WINDOW_WIDTH'] - self['SIDE_PANEL_WIDTH']

        def land_cell_height():
            #LAND_CELL_HEIGHT = WINDOW_HEIGHT // LAND_NUM_Y
            return self['WINDOW_HEIGHT'] // self['LAND_NUM_Y']

        def build_func():
            return (side_panel_width,field_width,land_cell_height)

        def build_names(func_list):
            return tuple([parse_func_name(i) for i in func_list])

        #body:
        if not name:
            self.calc_func = build_func()
            self.calc_names = build_names(self.calc_func)
            return None

        name = name.lower()
        assert name in self.calc_names, 'Constant with name "' + name +\
            '" does not exist.'
        index = self.calc_names.index(name)

        return self.calc_func[index]()

    def __del__(self):
        '''
        Closes DB connection when deleted
        '''
        self.db_cursor.close()

class Logger:
    """Class that performs all logging in game """

    def __init__(self):
        '''
        (self) -> None

        Initialization and new file creation
        '''
        self.log_file = None

        #Defining log file name for current session
        files = glob.glob(LOG_DIR + '*')
        if len(files):
            index = int(max(files)[len(LOG_DIR):-4]) +1
            if index < 10:
                index = '0' + str(index)
            else:
                index = str(index)
            file_name = LOG_DIR + index + '.txt'
        else:
            file_name = LOG_DIR + '01.txt'

        #Creatin log file
        self.log_file = open(file_name, 'w')
        self.log_file.write('==============Stone Age log==============\n')

        return None

    def append(self, line, console = True, log = True):
        '''
        (str, bool, bool) -> None

        Adds line in log and Python console.
        '''
        if console:
            print(line)
        if log:
            self.log_file.write(line + '\n')

        return None

    def finalize(self):
        '''
        (None) -> None

        Closes logging session.
        '''

        self.log_file.write('==============Stone Age is closed==============')
        self.log_file.close()

        return None


def cellToPxCoordinate(cell_coordinates):
    px_coordinates = (cell_coordinates[0] * LAND_CELL_WIDTH+LAND_CELL_WIDTH // 2,
                      cell_coordinates[1] * LAND_CELL_WIDTH+LAND_CELL_HEIGHT // 2)
    return px_coordinates

def pxToCellCoordinate(coordinates):
    px_coordinates = ((coordinates[0] - coordinates[0] % LAND_CELL_WIDTH) // LAND_CELL_WIDTH,
                      (coordinates[1] - coordinates[1] % LAND_CELL_WIDTH) // LAND_CELL_WIDTH)
    return px_coordinates

def file_exists(path ,filename):
    '''
    (str,str) -> bool

    Return True if file exists in following directory
    '''
    files = glob.glob(path + '*')
    for file in files[:]:
        files.remove(file)
        files.append(file[len(path):])

    return filename in files

def db_backup():
    '''
    (None) -> None

    Backup DB file on daily basis.
    '''
    date = int(time.time() / 86400)
    if file_exists('database\\backup\\','date'):
        file=open('database\\backup\\date', 'r')
        last_date = file.readline()
        file.close()
        last_date = int(last_date)
        if date == last_date:
            return None
    shutil.copy('database\\core.db','database\\backup\\core' + str(date) + '.db')
    file=open('database\\backup\\date', 'w')
    file.write(str(date))
    file.close()






'''
if __name__ == '__main__':
    main() 
'''