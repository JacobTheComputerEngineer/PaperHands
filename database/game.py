from . import database, account
from typing import List, Dict
from datetime import datetime

class Game():
    def __init__(
        self,
        gameID: str, 
        privacy, 
        money: float, 
        startTime: datetime, 
        endTime: datetime,
        ):
        
        self.gameID = gameID
        self.players: List[str] = list()
        
        # Format is the following
        #   Key: Player Name
        #       Value: Dict of Trades
        #           Key: Ticker Name
        #           Value: Number of shares
        self.trades: Dict[str, Dict[str, float]] = dict()
        
        # Format is the following
        #   Key: Player Name
        #       Value: Balance
        self.balances: Dict[str, float] = dict()
        
        self.db = None
        
        # game settings
        self.privacy = privacy # The type of this isnt well defined
        self.starting_money = money
        self.start_time = startTime
        self.end_time = endTime
    
    """
    Adds a player to the game 
    """
    def addPlayer(self, user: account.UserAccount):
        self.players.append(user.username)
        user.games.append(self.gameID)
        self.trades[user.username] = dict()
        self.balances[user.username] = self.starting_money
        
        self.db.addUserToGame(user, self)
        
        
    
    """
    Stops the game and removes it from the database
    """
    def endGame(self):
        
        # determine winner
        max_balance = 0
        max_player = ""
        for player, balance in self.balances.items():
            if balance > max_balance:
                max_balance = balance
                max_player = player
        
        # increment winner win count
        self.db.getUser(player).num_wins += 1
        
        for player in self.players:
            # update player information
            player = self.db.getUser(player)
            
            player.num_games += 1
            player.game_history.append((self.gameID, max_player))
            self.db.updateUser(player)
            
            self.db.removeUserFromGame(player, self)
            
        self.db.removeGame(self)
    
    """
    Gets the balance of a player, if the player is not in the game, then returns None
    """
    def getPlayerBalance(self, username: str) -> float:
        if username not in self.players:
            return None
        
        return self.balances[username]
    
    #TODO: have some way of signaling nonexisting player vs insufficient balance (probably use a exceptions)
    """
    Adds a ticker to the users account, updates the trade log and the balance, 
    if the player has an insufficent balance returns None, otherwise return new balance
    if the player is not in this game return None
    """
    def buyTicker(self, user: account.UserAccount, ticker: str, shares: float, price: float):
        if user.username not in self.players:
            return None
        if self.balances[user.username] < shares * price:
            return None
        if ticker not in self.trades[user.username]:
            self.trades[user.username][ticker] = 0
        # good trade
        self.balances[user.username] -= shares * price
        self.trades[user.username][ticker] += shares
        self.db.updateGame(self)
        return self.getPlayerBalance(user.username)
    
    """
    Removes a ticker to the users account, updates the trade log and the balance
    if the player is not in this game return None,
    if the player does not possess enough shares return None without changes,
    Otherwise return new balance
    """
    def sellTicker(self, user: account.UserAccount, ticker: str, shares: float, price: float):
        if user.username not in self.players:
            return None
        if ticker not in self.trades[user.username]:
            return None
        if self.trades[user.username][ticker] < shares:
            return None
        
        # good trade
        self.balances[user.username] += shares * price
        self.trades[user.username][ticker] -= shares
        self.db.updateGame(self)
        return self.getPlayerBalance(user.username)