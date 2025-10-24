from . import database, account
from typing import List

class Settings():
    def __init__(self, privacy, money, startTime, endTime):
        self.privacy = privacy
        self.money = money
        self.startTime = startTime
        self.endTime = endTime

class Game():
    def Game(self, settings: Settings, gameID: str):
        self.gameID = gameID
        self.settings = settings
        self.players: List[account.UserAccount] = list()
        
        self.db = None
        
    def addPlayer(self, user: account.UserAccount):
        self.players.append(user)
        self.db.addUserToGame(user.username, self.gameID)
    
    def endGame(self):
        for player in self.players:
            self.db.removeUserFromGame(player.username)
            
        self.db.removeGame()