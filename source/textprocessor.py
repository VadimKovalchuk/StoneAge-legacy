import glob

#CONSTANTS
#Uplading constants from setup.ini file
from source import tools
constants = {}
constants = tools.importConstants()
'''___________________________________________________________'''
#Game directories
CONTROLS_DIR     = constants['CONTROLS_DIR']    #Default is 'controls\\'
del constants
TXT_SUBFOLDER = 'text\\'
LANGUAGE = 'EN'

POPUP_ORDER ={
    'daily':    [1101,1301,1304,1303,1302,1201,1202],
    'nightly':  [1305,1203,1306,1204]
}
'''___________________________________________________________'''

class TextProcessor:
    """Class that handles translation and text output """

    def __init__(self):
        '''
        (self) -> None

        Initialization and loading all required language files
        '''
        self.controls = None
        self.translate_required = False
        self.translate = {}

        #Build basic controls table
        file_name = CONTROLS_DIR + TXT_SUBFOLDER + CONTROLS_DIR[:-1] + \
                    '_' + LANGUAGE + '.txt'
        self.controls = self._built_table(file_name)
        #print(self.controls)

        #buliding translate table if language is other than english
        if LANGUAGE != 'EN':
            self.translate_required = True
            file_name = CONTROLS_DIR + TXT_SUBFOLDER + CONTROLS_DIR[:-1] + \
                        '_' + 'EN' + '.txt'
            temp = self._built_table(file_name)
            for key in self.controls:
                if key > 1000:
                    break
                self.translate[temp[key]] = self.controls[key]

        return None

    def _built_table(self,file_name):
        '''
        (str) -> dict

        Builds text dictionary from the file.
        '''
        result_dict = {}
        file = open(file_name,'r')
        for line in file:
            assert ':' in line, \
                   'Incorrect text file syntax(":" character is missing)'
            [key, value] = line.split(':')
            result_dict[int(key)] = value[:-1]

        return result_dict

    def get_txt(self, table, id):
        '''
        (int) -> str

        Get text with passed ID from table.
        '''
        if table == 'controls':
            tab = self.controls
        else:
            assert False, 'Invalid table parameter passed to text processor.'
        if id in tab:
            return tab[id]
        else:
            return 'INVALID TEXT ID'

    def translator(self,sentence):
        '''
        (str) -> str

        Checks string for words from translation dictionary, and replaces
        it with translate. If translate is not required - return sentence.
        '''
        if not self.translate_required:
            return sentence

        for word in self.translate:
            if word in sentence:
                sentence = sentence.replace(word, self.translate[word])

        return sentence

    def popup(self, obj):
        '''
        (obj) -> str

        Generates report for daily popup.
        '''
        message_dict = obj.popup
        assert 'type' in message_dict, '"type" item is not found in popup dictionary'
        popup_type = message_dict['type'][0]
        del message_dict['type']
        text = ''

        for message_id in POPUP_ORDER[popup_type]:
            if message_id in message_dict:
                text += self._gen_popup_text(message_id,message_dict[message_id])
                del message_dict[message_id]
        if 'hunt' in text:
            text = text.replace('hunt','wildfowl')
        text = self.translator(text)

        obj.raise_popup = False
        text = self._fit_length(text)
        print(popup_type.capitalize() + ' popup:\n' + text)
        return text

    def _gen_popup_text(self,message_id, arguments):
        '''
        (int, list) -> str

        Generate text according to message type and list of arguments.
        Message types:
            - text before argument  (1101 .. 1199)
            - text only             (1201 .. 1299)
            - argument before text  (1301 .. 1399)
        If list contains elements of str type - they are concatenated.
        If list contains elements of int type - sum will be displayed.
        '''
        arg_type = str(type(arguments[0]))[-5:-2]
        assert arg_type in ('str','int'), 'Incorrect list passed to text processor'
        if arg_type == 'str':
            arg_str = ', '.join(arguments)
        else:
            arg_str = str(sum(arguments))

        if 1101 <= message_id < 1200:
            return self.get_txt('controls', message_id) + arg_str + '.\n'
        elif 1201 <= message_id < 1300:
            return self.get_txt('controls', message_id) + '.\n'
        elif 1301 <= message_id < 1400:
            return arg_str + self.get_txt('controls', message_id) + '.\n'
        else:
            return 'INCORRECT MESSAGE ID'

    def _fit_length(self, text):
        '''
        (str) -> str

        Adds newline character in lines that longer than popup text field width.
        '''
        changes = False
        lines = text.split('\n')
        limit = 43
        for line in lines:
            if len(line) > limit:
                line_index = lines.index(line)
                for i in range(1,limit // 2):
                    if line[limit - i] == ' ':
                        lines[line_index] = line[:limit - i] + '\n' + line[limit - i + 1:]
                        #lines[line_index][limit - i] = '\n'
                        changes = True
                        break
                else:
                    lines[line_index] = line[:limit] + '\n' + line[limit:]
                    changes = True

        text = '\n'.join(lines)
        if changes:
            text = self._fit_length(text)

        return text





































