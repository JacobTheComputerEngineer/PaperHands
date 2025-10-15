from . import database, account
from typing import List

class Game():
    def Game(self, gameID: str):
        self.gameID = gameID
        self.players: List[account.UserAccount] = list()
        
        self.db = None
        
    def addPlayer(self, user: account.UserAccount):
        self.players.append(user)
        self.db.addUserToGame(user.username, self.gameID)
    
    def endGame(self):
        for player in self.players:
            self.db.removeUserFromGame(player.username)
            
        self.db.removeGame()