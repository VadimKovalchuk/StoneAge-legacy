import sqlite3
from source import skilltree

#CONSTANTS
#Uplading constants from setup.ini file
from source import tools
constants = {}
constants = tools.importConstants()
'''___________________________________________________________'''
#Active language
LANGUAGE        = constants['LANGUAGE']
DB_DIR = 'database\\'
del constants

POPUP_ORDER ={
    'daily':    [2001,4001,4004,4003,4002,3001,3002],
    'nightly':  [4005,3003,4006,3004]
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
        db = sqlite3.connect(DB_DIR + 'core.db')
        self.db_cursor = db.cursor()

        #buliding translate table if language is other than english
        if LANGUAGE != 'EN':
            self.translate_required = True
            self.db_cursor.execute('SELECT en,' + LANGUAGE +\
                                   ' FROM controls WHERE id > 0 and id <= 1000')
            for row in self.db_cursor.fetchall():
                self.translate[row[0]] = row[1]

        return None

    def get_txt(self, table, id):
        '''
        (int) -> str

        Get text with passed ID from table.
        '''
        assert table in ('controls','items'), \
            'Invalid table parameter passed to text processor.'
        self.db_cursor.execute('SELECT ' + LANGUAGE + ' FROM ' + table +\
                               ' WHERE id =' + str(id))
        row = self.db_cursor.fetchone()
        if row:
            return row[0]
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

        if popup_type in POPUP_ORDER.keys():
            for message_id in POPUP_ORDER[popup_type]:
                if message_id in message_dict:
                    text += self._gen_popup_text(message_id,message_dict[message_id])
                    del message_dict[message_id]
            if 'hunt' in text:
                text = text.replace('hunt','wildfowl')
            text = self.translator(text)
        elif 'skill' in popup_type:
            assert 'skill' in message_dict, 'Popup for Skill is called, but ID is not passed.'
            skill = skilltree.Skill(None,message_dict['skill'])
            text += self.get_txt('controls', skill.name) + '.\n'
            if 'info' in popup_type:
                text += self.get_txt('controls', skill.description) + '.\n'
            elif 'done' in popup_type:
                text += self.get_txt('controls', skill.learned) + '.\n'
            else:
                assert False, 'Incorrect Skill popup parameter:' + popup_type

        obj.popup = {}
        obj.raise_popup = False
        text = self._fit_length(text)
        #print(popup_type.capitalize() + ' popup:\n' + text)
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

        if 2001 <= message_id < 3000:
            return self.get_txt('controls', message_id) + arg_str + '.\n'
        elif 3001 <= message_id < 4000:
            return self.get_txt('controls', message_id) + '.\n'
        elif 4001 <= message_id < 5000:
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





































