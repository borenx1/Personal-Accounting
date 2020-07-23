class Transaction:

    #t_type is a number, date is datetime.date object
    def __init__(self, amount, name, t_type, date):
        self.__amount = amount
        self.__name = name
        self.__type = t_type
        self.__date = date

    def __str__(self):
        return self.__name + ': ' + str(self.__amount) + ' (' +\
               type_to_text(self.__type) + ') ' + str(self.__date)

    def get_amount(self):
        return self.__amount

    def get_name(self):
        return self.__name

    def get_type(self):
        return self.__type

    def get_typestr(self):
        return type_to_text(self.__type)

    def get_date(self):
        return self.__date

    def set_amount(self, amount):
        self.__amount = amount

    def set_name(self, name):
        self.__name = name

    def set_type(self, t_type):
        self.__type = t_type

    def set_date(self, date):
        self.__date = date

def type_to_text(type_num):
    if isinstance(type_num, int):
        if type_num == 1:
            return 'Needed Expense'
        elif type_num == 2:
            return 'Extra Expense'
        elif type_num == 3:
            return 'Income'
        elif type_num == 4:
            return 'Special Expense'
        elif type_num == 5:
            return 'Bonus'
        else:
            raise ValueError('Choose a correct integer ' + str(type_num))
    else:
        raise TypeError('Wrong type :/')
