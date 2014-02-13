import sqlite3

DB_DIR = 'database\\'

def _build_list(line):
    '''
    (str) -> list of ints

    Slits line by ',' and converts to int
    '''
    if not line:
        return None
    lst = line.split(',')
    for i in range(0,len(lst)):
        lst[i] = int(lst[i])
    return lst

class SkillTree:
    """ Defines tribe technological advance. Helper class for Tribe class."""
    
    def __init__(self, Tribe):
        '''
        (Tribe)-> None

        Defines starting state.
        '''
        self.Tribe = Tribe
        self.skills = []
        self.available_skills = []
        self.learned = None
        self.active_skills = []
        self.available_items = []
        db = sqlite3.connect(DB_DIR + 'core.db')
        self.db_cursor = db.cursor()

        for i in range(1,7):
            self.skills.append(Skill(self, i))

        self.db_cursor.execute('SELECT id FROM skills WHERE dependencies is NULL')
        ids = self.db_cursor.fetchall()
        for id in ids:
            self.available_skills.append(Skill(self, id[0]))

        return None

    def set_learned(self, id):
        '''
        (int) -> None

        Set Skill with passed ID to be mastered in day phase.
        Assert error if Skill is no available in available skills.
        '''
        skill = self._is_available(id)
        assert skill,'Mastered Skill with ID'+str(id)+\
                                      ' is missing in available skills list'
        self.learned = skill

        return None

    def master_skill(self):
        '''
        (None) -> None

        Master Skill that set as learned.
        When Skill is mastered:
         - it removed from available skills list
         - database is checked for new available skills that has dependency
            for mastered.
         - items that opened by resource  - added to available items list
        '''
        assert self.learned,'No Skill is set for mastering'
        self.active_skills.append(self.learned.id)
        self.available_skills.remove(self.learned)
        available_ids = self._track_dependencies(self.learned.id)
        for new_id in available_ids:
            self.available_skills.append(Skill(self,new_id))

        return None

    def _track_dependencies(self,id):
        '''
        (int) -> list of ints

        Search Skills that dependent from skill with passed id and returns
        them as a list.
        '''
        skills = []
        self.db_cursor.execute('SELECT id,dependencies FROM skills WHERE dependencies  LIKE "%'\
                               + str(id) + '%"')
        rows = self.db_cursor.fetchall()
        for row in rows:
            dependencies = _build_list(row[1])
            if id in dependencies:
                available = True
                for skill in dependencies:
                    if skill not in self.active_skills:
                        available = False
                if available:
                    skills.append(row[0])

        return skills

    def _is_available(self, id):
        '''
        (int) -> bool

        Return skill with passed id if it is present in available skills
        otherwise returns False.
        '''
        for skill in self.available_skills:
            if skill.id == id:
                return skill
        return False

    def __str__(self):
        return self.Tribe.name + ' SkillTree'

class Skill:
    """ Defines skill class with requirements and possibilities.
        Helper class for SkillTree."""

    def __init__(self, SkillTree, id):
        '''
        (SkillTree) -> None

        Builds skill data from file in skill directory.
        '''
        skill = self.import_skill(id)
        self.id = id                            #Skill id
        self.SkillTree = SkillTree              #Skill tree that Skill belongs to
        self.name = skill['name']               #Skill name
        self.description = skill['description'] #Skill description for skill tree
        self.experience = skill['experience']   #What should be done before skill can be learned
        self.price = skill['price']             #items that required for skill learning
        self.dependencies = skill['dependencies']#Condition skills required for current one to become available
        self.items = skill['items']             #Items that becomes available in workshop after skill learning
        self.learned = skill['learned']         #Text that will be displayed when text is learned

        #print(self.get_exp())

        return None

    def import_skill(self, id):
        '''
        (int) -> None

        Validates skill file that corresponds to skill id. In case of any
        errors asserts error message.
        '''
        db = sqlite3.connect(DB_DIR + 'core.db')
        cursor = db.cursor()
        cursor.execute('SELECT * FROM skills WHERE id =' + str(id))
        row = cursor.fetchone()
        db.close()
        result = {}
        result['name']= row[1]
        result['description'] = row[2]
        result['experience'] = self._build_dict(row[3])
        result['price'] = self._build_dict(row[4])
        result['dependencies'] = _build_list(row[5])
        result['items'] = _build_list(row[6])
        result['learned'] = row[7]


        return  result

    def _build_dict(self,line):
        '''
        (str) -> dict
        First splits by ',' on pairs, than splits on key and value by ':'.
        Final values converted to int.
        '''
        if not line:
            return None
        dictionary = {}
        pairs = line.split(',')
        for pair in pairs:
            key,value = pair.split(':')
            if key.isnumeric():
                key = int(key)
            if value.isnumeric():
                value = int(value)
            dictionary[key] = value

        return dictionary



    def get_exp(self):
        '''
        (None) -> dict

        Returns resource, obtained and required experience. If requirements
        are multiple, returns first one.
        '''
        for key in self.experience:
            value = self.experience[key]
            if key not in self.SkillTree.Tribe.statistics:
                self.SkillTree.Tribe.statistics[key] = 0
            obtained = self.SkillTree.Tribe.statistics[key]
            if obtained < value:
                return {'resource':key,
                        'required':value,
                        'obtained':obtained}
        return 'done'

    def get_price(self):
        '''
        (None) -> dict

        Returns price required for mastering skill
        '''
        price = {}
        for resource in self.price:
            cost = self.price[resource]
            if 'Px' in cost:
                multiplier = int(cost[-1])
                cost = len(self.SkillTree.Tribe.population) * multiplier
            price[resource] = cost

        return price

    def affordable(self):
        '''
        (None) -> bool

        Verifies if there are enough resources to master current Skill.
        Returns True if yes.
        '''
        price = self.get_price()
        for resource in price:
            if resource.isnumeric():
                pass #Will be compleate after Workshop implementation
            if price[resource] > self.SkillTree.Tribe.get_resource(resource):
                return False

        return True

    def __str__(self):
        return 'Skill id=' + str(self.id) + ', name=' + str(self.name)


