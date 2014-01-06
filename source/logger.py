import glob

LOG_DIR = 'log\\'

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