class User:
    def __init__(self):
        self.__id_user = None
        self.__username = None
        self.__password = None
        self.__name = None
        self.__lastname = None
        self.__email = None
        
    @property
    def id(self):
        return self.__id_user

    @id.setter
    def id(self, _id):
        self.__id_user = _id 

    @property
    def username(self):
        return self.__username
    
    @username.setter 
    def username(self, _username):
        self.__username = _username

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, _password):
        self.__password = _password

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, _name):
        self.__name = _name
    
    @property
    def lastname(self):
        return self.__lastname

    @lastname.setter
    def lastname(self, _lastname):
        self.__lastname = _lastname

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, _email):
        self.__email = _email