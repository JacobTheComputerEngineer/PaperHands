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
        #       Value: Dict of Trades
        #           Key: Ticker Name
        #           Value: Average price of share
        self.avg_price: Dict[str, Dict[str, float]] = {}
        
        # Format is the following
        #   Key: Player Name
        #       Value: Balance
        self.balances: Dict[str, float] = dict()
        
        self.db = None
        
        # game settings
        self.privacy = privacy  # The type of this isnt well defined
        self.starting_money = float(money)
        self.start_time = startTime
        self.end_time = endTime
    
    """
    Adds a player to the game 
    """
    def addPlayer(self, user: account.UserAccount):
        # Maybe add check if user == None?
        self.players.append(user.username)
        user.games.append(self.gameID)
        self.trades[user.username] = dict()
        self.avg_price[user.username] = dict()
        self.balances[user.username] = self.starting_money
        
        self.db.addUserToGame(user, self)
        
    """
    Removes a player from the game, if player not in game does nothing
    """
    def removePlayer(self, user: account.UserAccount):
        if user.username not in self.players:
            return
        
        self.players.remove(user.username)
        user.games.remove(self.gameID)
        
        self.trades.pop(user.username, None)
        self.avg_price.pop(user.username, None)
        self.balances.pop(user.username, None)
        
        self.db.removeUserFromGame(user, self)
    
    """
    Stops the game and removes it from the database
    """
    def endGame(self):
        
        # sell all tickers before determining winner
        for players in self.players:
            #for each ticker the player holds
            held_tickers = self.trades[players]
            for tickers in held_tickers.keys():
                self.sellTicker(self.db.getUser(players), tickers, held_tickers[tickers])
        
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
    if price is none will use the value given from finnhub
    if the player has an insufficent balance returns None, otherwise return new balance
    if the player is not in this game return None
    """
    def buyTicker(self, user: account.UserAccount, ticker: str, shares: float, price: float = None):
        # user must be in the game
        if user.username not in self.players:
            return None

        # make sure this user has a balance entry
        if user.username not in self.balances:
            self.balances[user.username] = float(self.starting_money)

        # make sure this user has a trades dict
        if user.username not in self.trades:
            self.trades[user.username] = {}

        # make sure this user has an avg_price dict
        if user.username not in self.avg_price:
            self.avg_price[user.username] = {}

        if price is None:
            price = user.get_price(ticker)

        cost = shares * price
        if self.balances[user.username] < cost:
            return None

        old_shares = self.trades[user.username].get(ticker, 0.0)
        old_avg = self.avg_price[user.username].get(ticker)

        # good trade
        new_total_shares = old_shares + shares
        if new_total_shares <= 0:
            new_avg = price
        else:
            if old_avg is None or old_shares <= 0:
                new_avg = price
            else:
                # volume-weighted average price
                new_avg = (old_avg * old_shares + price * shares) / new_total_shares

        self.trades[user.username][ticker] = new_total_shares
        self.balances[user.username] -= cost
        self.avg_price[user.username][ticker] = new_avg

        self.db.updateGame(self)
        return self.getPlayerBalance(user.username)

    """
    Removes a ticker to the users account, updates the trade log and the balance
    if price is none will use the value given from finnhub
    if the player is not in this game return None,
    if the player does not possess enough shares return None without changes,
    Otherwise return new balance
    """
    def sellTicker(self, user: account.UserAccount, ticker: str, shares: float, price: float = None):
        if user.username not in self.players:
            return None

        # if we somehow have no trades recorded for this user, nothing to sell
        if user.username not in self.trades:
            return None

        if ticker not in self.trades[user.username]:
            return None

        if self.trades[user.username][ticker] < shares:
            return None
        
        # good trade
        if price is None:
            price = user.get_price(ticker)
        
        self.balances[user.username] += shares * price
        self.trades[user.username][ticker] -= shares
        self.db.updateGame(self)
        return self.getPlayerBalance(user.username)

    """
    Returns the (unrealized) Profit Loss from a single ticker
    """
    def getProfitLoss(self, user: account.UserAccount, ticker: str):
        if user.username not in self.trades:
            return None

        if ticker not in self.trades[user.username]:
            return None
        
        shares = self.trades[user][ticker]
        avg = self.avg_price[user][ticker]
        current = self.db.getUser(user).get_price(ticker)
        return (current - avg) * shares
    
    """
    Returns the average price of a single ticker
    """
    def getAvgPrice(self, user:account.UserAccount, ticker:str):
        if user.username not in self.trades:
            return None

        if ticker not in self.trades[user.username]:
            return None
        
        return self.avg_price[user.username][ticker]
    
    """
    Returns a list of positions held by the player
    """
    def getPositions(self, user:account.UserAccount):
        if user.username not in self.trades:
            return None

        return self.trades[user.username]
    