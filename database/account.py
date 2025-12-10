"""
Account.py
Eric Yung, November 21 2025

Class which stores information about any particular user
"""

import finnhub
from enum import Enum

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
        
        #TODO: catch API key exceptions and figure out correct behavior
        self.api_key = api_key
        try:
            self.finn_client = finnhub.Client(self.api_key)
        except:
            print("Warning: Invalid API Key")
            
        
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
    
    """
    Gets a ticker and returns a dictionary of information about the ticker
    If the ticker is not valid returns None
    """
    def get_ticker(self, ticker:str) -> dict:
        profile = self.finn_client.company_profile2(symbol=ticker)
        if not profile or "name" not in profile:
            #not valid
            return None
        
        # get data
        quote = self.finn_client.quote(ticker)
        data = {
            TickerValues.NAME: profile.get("name", "N/A"),
            TickerValues.TICKER_SYMBOL: ticker,
            TickerValues.PRICE: quote.get("c", 0.0),
            TickerValues.PRICE_CHANGE: quote.get("o", 0.0),
            TickerValues.PRICE_HIGH: quote.get("h", 0.0),
            TickerValues.PRICE_LOW: quote.get("l", 0.0),
            TickerValues.PREV_CLOSE_PRICE: quote.get("pc", 0.0),
        }
        
        return data
    
    """
    Gets the current price of a given ticker
    """
    def get_price(self, ticker:str) -> float:
        return self.get_ticker(ticker)[TickerValues.PRICE]
    
class TickerValues(Enum):
    NAME = "name"
    TICKER_SYMBOL = "symbol"
    PRICE = "price"
    PRICE_CHANGE = "price_change"
    PRICE_HIGH = "high"
    PRICE_LOW = "low"
    PREV_CLOSE_PRICE = "previous_close_price"