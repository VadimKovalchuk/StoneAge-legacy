from source import tools
import random, sqlite3

ITEMS_DIR = 'items\\'
DB_DIR = 'database\\'

class Item:
    """ All kinds of goods that can be worn, dressed or carried by tribesmen """

    def __init__(self, id, parameters = None):
        '''
        (int, dict) -> None

        Creates item according to id. Fills all parameters for newly
        created item with default values. if some parameters are passed -
        assigns them.
        '''
        item = self._import_item_db(id)
        self.id = id                        #item id
        self.owner = None                   #Item owner
        self.name = item['name']            #Item name
        self.type = item['type']            #Item type
        self.points = item['points']        #e.g. amount of damage for weapon or armor for wear.
        self.durability = item['durability']#Damage amount that can be dealt or taken by item.
        self.consumable = item['consumable']#Consumable item list that required for item usage.
        self.amount = item['amount']        #Consumable items and ingredients can be stacked.
        self.description = item['description']#Item description for tech tree and workshop.
        self.ingredients = item['ingredients']#Ingredients that required for item creation.

        return None

    def _import_item_db(self,id):
        '''
        (int) -> dict

        Returns dictionary where field name is a key and field value is the one.
        '''
        id = str(id)
        db = sqlite3.connect(DB_DIR + 'core.db')
        cursor = db.cursor()
        cursor.execute('SELECT * FROM items WHERE id =' + str(id))
        row = cursor.fetchone()
        db.close()
        result = {}
        result['name']= row[1]
        result['type'] = row[2]
        result['points'] = [i for i in range(row[3],row[4] + 1)]
        result['durability'] = row[5]
        if row[6]:
            param_list = row[6].split(',')
            value = []
            for item in param_list:
                value.append(int(item))
            result['consumable'] = value
        else:
            result['consumable'] = None
        result['description'] = row[7]
        ingredients_list = row[8].split(',')
        result['ingredients'] = {}
        for ingredient in ingredients_list:
            name,amount = ingredient.split(':')
            if name.isnumeric():
                name = int(name)
            result['ingredients'][name] = int(amount)
        result['amount'] = row[9]

        return  result


    def __str__(self):

        string = 'ID' + str(self.id)
        if self.type == 'consumable':
            string += 'x' + str(self.amount)
        else:
            string += '('+ str(self.durability) + ')'

        return string

    def hit(self):
        '''
        (None) -> int

        If current item is a weapon randomly returns damage from points list.
        '''
        assert self.type == 'weapon','Non weapon item is called for hit method'
        assert self.owner,'Item usage without owner'
        if self.consumable:
            pass
        else:
            amount = random.choice(self.points)
            if amount > self.owner.points:
                amount = self.owner.points
            self.durability -= 1
            print('generated',amount,'from',self.points,'. Durability', self.durability)

        return amount

    def expired_durability(self):
        '''
        (None) -> None

        Verifies if durability is lower than 1.
        '''
        return self.durability < 1


