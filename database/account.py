#TODO: this should probably be a struct instead
class UserAccount():
    def __init__(
            self, 
            username: str, 
            password: str = "", 
            api_key: str = "", 
            friends = [], 
            games = [], 
            game_history = [],
            num_games = 0,
            num_wins =0
        ):
        
        #TODO: Do passwords correctly with hashing
        self.username = username
        self.password = password
        self.api_key = api_key
        self.friends = friends
        self.games = games
        
        # format: list of
        #   (String, String)
        #   (GameID, Winner)
        self.game_history = game_history
        self.num_games = num_games
        self.num_wins = num_wins
        
        # used to update the databse whenever changes are made
        self.db = None
    
    def update_password(self, password: str):
        self.password = password
        self.db.updateUser(self)
        
    def update_api(self, api: str):
        self.api_key = api
        self.db.updateUser(self)
        
    def add_friend(self, friend: str):
        self.friends.append(friend)
        self.db.updateUser(self)
        
    def remove_friend(self, friend:str):
        self.friends.remove(friend)
        self.db.updateUser(self)