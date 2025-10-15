#TODO: this should probably be a struct instead
class UserAccount():
    def UserAccount(self, username: str, password: str = "", api_key: str = "", friends = [], games = []):
        #TODO: Do passwords correctly with hashing
        self.username = username
        self.password = password
        self.api_key = api_key
        self.friends = friends
        self.games = games
        
        # used to update the databse whenever changes are made
        self.db = None
    
    def update_password(self, password: str):
        self.password = password
        self.db.updateUser(self)
        
    def update_api(self, api: str):
        self.api = api
        self.db.updateUser(self)
        
    def add_friend(self, friend: str):
        self.friends.append(friend)
        self.db.updateUser(self)
        
    def remove_friend(self, friend:str):
        self.friends.remove(friend)
        self.db.updateUser(self)