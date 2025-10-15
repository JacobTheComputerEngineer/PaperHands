from pymongo import MongoClient
from . import account, game, dbKeys

class DB:
    
    def __init__(self, db: MongoClient):
        self.db = db
        self.userdb = db[dbKeys.user_collection]
        self.gamedb = db[dbKeys.games_collection]
        
        # ensures no duplicate users are made
        # format: Username: Account
        self.active_users = {}
    
    """
    Returns the user from the record if it exists in the record already,
    If it doesnt then make a new record and add it then return to record
    If the user doesnt exist, creates a new user with that name with empty records and returns it
    """
    def getUser(self, username:str):
        
        if username in self.active_users:
            return self.active_users[username]
        else:
            user_record = self.userdb.find_one({dbKeys.username:username})
            
            if user_record is None:
                # case where no user, create a new one and return it
                new_user = account.UserAccount(username)
                new_user.db = self
                self.active_users[username] = new_user
                return new_user
            
            #standard case, find user in DB then add it to record
            new_user = account.UserAccount(
                user_record[dbKeys.username],
                user_record[dbKeys.password],
                user_record[dbKeys.api_key],
                user_record[dbKeys.friends],
                user_record[dbKeys.games_list_key],
            )
            new_user.db = self
            
            self.active_users[username] = new_user
            
            return new_user

    """
    Adds a new user to the databse then adds it to the record, if the user exists, does nothing and returns false,
    otherwise returns true
    """
    def addUser(self, newuser: account.UserAccount):
        
        if self.userdb.find_one({dbKeys.username: newuser.username}) is not None:
            return None
        
        self.userdb.insert_one(
            {dbKeys.username:newuser.username, 
             dbKeys.password:newuser.password,
             dbKeys.api_key: newuser.api_key,
             dbKeys.friends: newuser.friends,
             dbKeys.games_list_key: newuser.games
             })
        
        newuser.db = self
        
        self.active_users[newuser.username] = newuser
        return True
    
    """
    Adds a single user to a game
    """
    def addUserToGame(self, user: account.UserAccount, game: game.Game):
        #TODO: add error checking, maybe use _id instead of id for both user and gameID
        #TODO: add error checking for no user found in DB
        self.userdb.update_one(
            {
                dbKeys.username: user.username
            },
            {
                "$addToSet":{dbKeys.games_list_key: game.gameID}
            })
        
        self.gamedb.update_one(
            {
                dbKeys.game_id: game.gameID
            },
            {
            "$addToSet":{dbKeys.users_list_key: user.username}
            })
    
    """
    Removes a single user from a game
    """    
    def removeUserFromGame(self, user: account.UserAccount, game: game.Game):
        #TODO: add error checking for no user found in DB
        self.gamedb.update_one(
            {
                dbKeys.game_id: game.gameID
            },
            {
                "$pull":{dbKeys.users_list_key: user.username}
            })
        
        self.userdb.update_one(
            {
            dbKeys.username: user.username
            },
            {
            "$pull": {dbKeys.games_list_key: game.gameID}
            })
        
    
    """
    Removes all users from a game and then removes the game
    """
    def removeGame(self, game: game.Game):
        
        #get players and remove all players if any left
        for users in game.players:
            self.removeUserFromGame(users, game)
            
        #remove leftover game
        self.gamedb.delete_one({dbKeys.game_id: game.gameID})
    
    """
    Adds game to database
    returns true if game was added, false if game already exists
    """
    def addGame(self, game: game.Game):
        if self.gamedb.find_one({dbKeys.game_id: game.gameID}) is not None:
            return False

        self.gamedb.insert_one(
            {dbKeys.game_id: game.gameID,
             dbKeys.users_list_key: game.players
             })
        
        game.db = self
        
        return True
        
    """
    Updates a user if they exist, if they dont, adds them instead
    """
    def updateUser(self, user: account.UserAccount):
        
        if self.userdb.find_one({dbKeys.username: user.username}) is None:
            #doesnt exist in db yet, add to db
            self.addUser(user)
        else:
            self.userdb.update_one(
            {
                dbKeys.username: user.username
            },
            {
                "$set": {dbKeys.password: user.password,
                         dbKeys.api_key: user.api_key,
                         dbKeys.friends: user.friends,
                         dbKeys.games_list_key: user.games}
            })