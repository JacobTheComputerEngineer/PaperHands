#TODO: this should probably be a struct instead
class UserAccount():
    def UserAccount(self, username: str, password: str):
        #TODO: Do passwords correctly with hashing
        self.username = username
        self.password = password