from pymongo import MongoClient
from . import account, game

class DB:
    
    def userDB(self, db: MongoClient):
        self.db = db
        self.userdb = db["users"]
        self.gamedb = db["games"]
        
    def getUser(self, username:str):
        return self.userdb.find(username)

    def addUser(self, newuser: account.UserAccount):
        self.userdb.insert_one({"username":newuser.username, "password":newuser.password})
        
    def addUserToGame(self, user: account.UserAccount, game: game.Game):
        #TODO: add error checking, maybe use _id instead of id for both user and gameID
        user = self.userDB.find_one({"username": user.username})
        self.userdb.update_one({
            "username": user.username,
            "%addToSet":{"games": game.gameID}
            })
        
        self.gamedb.update_one({
            "gameID": game.gameID,
            "%addToSet":{"users": user.username}
            })
        
    def removeUserFromGame(self, user: account.UserAccount, game: game.Game):
        
        self.gamedb.update_one({
            "gameID": game.gameID,
            "%pull":{"users": user.username}
            })
        
        self.userDB.update_one({
            "username": user.username,
            "%pull": {"games": game.gameID}
        })