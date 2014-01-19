from source import tools
import random

ITEMS_DIR = 'items\\'

class Item:
    """ All kinds of goods that can be worn, dressed or carried by tribesmen """

    def __init__(self, id, parameters = None):
        '''
        (int, dict) -> None

        Creates item according to id. Fills all parameters for newly
        created item with default values. if some parameters are passed -
        assigns them.
        '''
        self.validate_item_file(id)
        item_file = self.import_item(id)
        self.id = id                        #item id
        self.owner = None                   #Item owner
        self.name = item_file['name']       #Item name
        self.type = item_file['type']       #Item type
        self.points = item_file['points']   #e.g. amount of damage for weapon or armor for wear.
        self.durability = item_file['durability']   #Damage amount that can be dealt or taken by item.
        self.consumable = item_file['consumable']   #Consumable item list that required for item usage.
        self.amount = item_file['amount']           #Consumable items and ingredients can be stacked.
        self.description = item_file['description'] #Item description for tech tree and workshop.
        self.ingredients = item_file['ingredients'] #Ingredients that required for item creation.

        return None

    def validate_item_file(self, id):
        '''
        (int) -> None

        Validates item file that corresponds to item id and returns true
        if file is OK.
        '''
        id = str(id)
        assert tools.file_exists(ITEMS_DIR,id + '.txt'), 'Invalid item ID'
        file = open(ITEMS_DIR + str(id) + '.txt','r')
        for line in file:
            assert '=' in line, \
                'Mandatory character "=" not found in item file:' + id
            key,value = line[:-1].split('=')
            assert key in ('name','type','points','durability','description',
                           'consumable','ingredients','amount'),\
                'Incorrect item parameter found in item file:' + id
            if key in ('name','durability','description','amount'):
                assert value.isnumeric(), \
                    'Incorrect parameter value in item file:' + id
            elif key in ('points','consumable'):
                param_list = value.split(',')
                for item in param_list:
                    assert item.isnumeric(),\
                        'Incorrect "points" parameter in item file:' + id
            elif key == 'ingredients':
                ingredients_list = value.split(',')
                for ingredient in ingredients_list:
                    name,amount = ingredient.split(':')
                    assert amount.isnumeric(), 'Space  found in item file:' + id
        file.close()

        return None

    def import_item(self,id):
        '''
        (int) -> dict

        Returns dictionary where field name is a key and field value is the one.
        '''
        id = str(id)
        item_dict = {}
        file = open(ITEMS_DIR + str(id) + '.txt','r')
        for line in file:
            key,value = line[:-1].split('=')
            if key in ('name','durability','description','amount'):
                value = int(value)
            elif key in ('points','consumable'):
                if key == 'consumable' and value == '0':
                    value = False
                else:
                    param_list = value.split(',')
                    value = []
                    for item in param_list:
                        value.append(int(item))
            elif key == 'ingredients':
                ingredients_list = value.split(',')
                value = {}
                for ingredient in ingredients_list:
                    name,amount = ingredient.split(':')
                    if name.isnumeric():
                        name = int(name)
                    value[name] = int(amount)

            item_dict[key] = value
        file.close()
        return  item_dict

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


