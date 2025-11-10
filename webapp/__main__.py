from flask import Flask, request, redirect, url_for, render_template, session, jsonify
import json
# from database import database as db
import time # easy gameID

from pymongo import MongoClient
from database import database, game, account

MONGO_PORT = 27017
MONGO_ADDR = "localhost"
mongo_db = MongoClient(f"mongodb://{MONGO_ADDR}:{MONGO_PORT}/")
app_database = database.DB(mongo_db["paperhands"])

app = Flask(__name__)

PORT = 5000

# It looks like we may need to do some HTML as well
# We can return render_template(html file, var=thing, var=thing)
# https://www.tutorialspoint.com/flask/flask_quick_guide.htm
# https://pythonbasics.org/flask-cookies/
# https://flask.palletsprojects.com/en/stable/quickstart/

'''
TODO
View old games / current games
Profile
Settings
Friends system

Game page
    Live updates - for demo
    All logic
'''

app.secret_key = b'SECRETKEYEXAMPLE' # quickstart says we need it, may be under the hood stuff

@app.route("/")
def landingRedirect():

    # If user logged in
    if 'username' in session:
        return redirect(url_for('homePage'))

    # Else user not logged in
    return redirect(url_for('loginPage'))

@app.route("/login", methods=['GET', 'POST'])
def loginPage():

    # Logged in already
    # if 'username' not in session:
    #     return redirect(url_for('createNewUser'))
    
    # Display page
    if request.method == 'GET':
        return render_template('login.html')
    
    elif request.method == 'POST':

        if request.form.get("useraction") == "New User":
            return redirect(url_for('createNewUser'))
        if request.form.get("useraction") == "Reset":
            return redirect(url_for('createNewUser'))

        # SANITIZE USER INPUTS
        un = request.form.get("Username")
        pw = request.form.get("Password")

        errs = []
        if un == "":
            errs.append("Missing username\n")
        if pw == "":
            errs.append("Missing password\n")

        # Errors username DNE and wrong password

        if errs:
            return render_template('login.html', errs=errs, erNo=len(errs))

        # print(un)
        # print(pw)

        # Check database
        user = app_database.getUser(un)
        # If in database
        if user is not None:
            if user.password == pw:
                session['username'] = un
                return redirect(url_for('homePage'))
            else:
                # Wrong password
                return redirect(url_for('loginPage'))
        else:
        # If not in database
            return redirect(url_for('loginPage'))

@app.route("/createAccount", methods=['GET', 'POST'])
def createNewUser():

    # Logged in already
    if 'username' in session:
        return redirect(url_for('homePage'))
    
    if request.method == 'GET':
        return render_template('createAccount.html')
    
    elif request.method == 'POST':
        # SANITIZE USER INPUTS
        un = request.form.get("Username")
        pw = request.form.get("Password")
        cw = request.form.get("Confirm Password")
        fk = request.form.get("Finnhub Key")

        errs = []
        if un == "":
            errs.append("Missing username\n")
        # CHEK UN DNE
        if pw == "":
            errs.append("Missing password\n")
        if cw == "":
            errs.append("Missing password confirmation\n")
        if pw != cw:
            errs.append("Passwords do not match\n")
        if fk == "":
            errs.append("Missing API key\n")
        # CHECK API KEY

        if errs:
            return render_template('createAccount.html', errs=errs, erNo=len(errs))
        
        session['username'] = un

        # If
        #   Username is new
        #   pw == cw
        #   fk is a properly working key
        user = app_database.getUser(un)
        
        if user is not None:
            # User already exists
            return redirect(url_for('createNewUser'))
        else:
            # Else create new user
            user = database.account.UserAccount(un, pw, fk)
            # TODO: Verify FK key
            app_database.addUser(user)
            return redirect(url_for('homePage'))

@app.route("/home", methods=['GET', 'POST'])
def homePage():

    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    if request.method == 'GET':
        return render_template('home.html', name=session['username'])
    
    elif request.method == 'POST':

        if request.form.get("Games"):
            return redirect(url_for('gamesPage'))
        
        if request.form.get("Profile"):
            return redirect(url_for('profilePage'))
        
        if request.form.get("Friends"):
            return redirect(url_for('friendsPage'))
        
        if request.form.get("Settings"):
            return redirect(url_for('settingsPage'))

        if request.form.get("Logout"):
            session.pop('username', None)
            return redirect(url_for('loginPage'))

@app.route("/games", methods=['GET', 'POST'])
def gamesPage():

    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    if request.method == 'GET':
        return render_template('gamesMenu.html')
    
    elif request.method == 'POST':

        if request.form.get("jg"):
            return redirect(url_for('joinGame'))
        
        if request.form.get("cg"):
            return redirect(url_for('currentGames'))
        
        if request.form.get("og"):
            return redirect(url_for('oldGames'))
        
        if request.form.get("ng"):
            return redirect(url_for('createGame'))
        
        if request.form.get("home"):
            return redirect(url_for('homePage'))

@app.route("/joingame", methods=['GET', 'POST'])
def joinGame():

    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    if request.method == 'GET':

        current_user = app_database.getUser(session['username'])
        games_list = app_database.getAllGames()
        game_id_list = list() # use this list to display all the games
        for game in games_list:
            if current_user.username in game.players:
                continue
            if game.privacy == "Public":
                game_id_list.append(game.gameID)
            elif game.privacy == "Friends":
            # look for if any are friends in this game
                is_friend = False
                for players in game.players:
                    game_user = app_database.getUser(players)
                    if current_user.username in game_user.friends:
                        is_friend = True
                        break
                if is_friend:
                    game_id_list.append(game.gameID)

        return render_template('joinGame.html', gameIDs=game_id_list)
    
    elif request.method == 'POST':
        
        if request.form.get("home"):
            return redirect(url_for('homePage'))
        
        if request.form.get("back"):
            return redirect(url_for('gamesPage'))
        
        gameID = request.form.get("join")
        if gameID:
            game_to_join = app_database.getGame(gameID)
            current_user = app_database.getUser(session['username'])
            game_to_join.addPlayer(current_user)
            return redirect(url_for('playGame', GAMEID=gameID))
    
    return "Join game"

@app.route("/activegames", methods=['GET', 'POST'])
def currentGames():

    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    if request.method == 'GET':
        current_user = app_database.getUser(session['username'])
        game_id_list = current_user.games
        # print(game_id_list)
        return render_template('activeGames.html', gameIDs=game_id_list)
    
    elif request.method == 'POST':
        
        if request.form.get("home"):
            return redirect(url_for('homePage'))
        
        gameID = request.form.get("go")
        if gameID:
            return redirect(url_for('playGame', GAMEID=gameID))
    
    # Display list of active games user is part of
    # Button to move to any game page
    # Back button

    # THIS WILL ALSO BE HEAVY

    # TODO: I didnt realize that we needed to store active/dead/not started games so for now this just
    # returns a list of games that the user is in
    
    # current_user = app_database.getUser(session['username'])
    # game_id_list = current_user.games
    
    
    # For every not completed game attached to the player
    #   Display it 
    #   Be able to click on it
    #       Move to playGame

    return "Active games"

@app.route("/oldgames", methods=['GET', 'POST'])
def oldGames():
    # TODO: Implement old games in DB
    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    if request.method == 'GET':
        return render_template('oldGames.html')
    
    elif request.method == 'POST':
        
        if request.form.get("home"):
            return redirect(url_for('homePage'))
    
    # Display list of any completed games user was part of
    # Button to view any of the pages
    # Back button

    # STILL HEAVY

     # TODO: I didnt realize that we needed to store active/dead/not started games so for now this just
    # returns a list of games that the user is in
    
    current_user = app_database.getUser(session['username'])
    game_id_list = current_user.games
    
    # For every completed game attached to the player
    #   Display it 
    #   Be able to click on it
    #       Move to playGame

    return "Old games"

@app.route("/newgame", methods=['GET', 'POST'])
def createGame():
    
    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    if request.method == 'GET':
        user = app_database.getUser(session["username"])
        friends = user.friends
        # friends_username = [f.username for f in friends]
        return render_template('newGame.html', friends=friends)
    
    elif request.method == 'POST':

        if request.form.get("back"):
            return redirect(url_for('gamesPage'))

        # SANITIZE USER INPUTS
        name = request.form.get("gameName")
        privacy = request.form.get("privacyStatus")
        money = request.form.get("moneyAmount")
        startTime = request.form.get("startTime")
        endTime = request.form.get("endTime")

        errs = []

        # print(privacy)
        # print(money)
        # print(startTime)
        # print(endTime)

        yr = time.localtime().tm_year
        mon = time.localtime().tm_mon
        day = time.localtime().tm_mday
        hr = time.localtime().tm_hour
        min = time.localtime().tm_min

        # print(yr, " ", startTime[:4])
        # print(mon, " ", startTime[5:7])
        # print(day, " ", startTime[8:10])
        # print(hr, " ", startTime[11:13])
        # print(min, " ", startTime[14:16])


        if privacy == None:
            errs.append("Missing privacy\n") # Fix new line

        if int(startTime[:4]) < yr: # Invalid year start
            errs.append("Start year too early\n")
        elif int(startTime[:4]) == yr: # This year, check others

            if int(startTime[5:7]) < mon:
                errs.append("Start month too early\n")
            elif int(startTime[5:7]) == mon:

                if int(startTime[8:10]) < day:
                    errs.append("Start day too early\n")
                elif int(startTime[8:10]) == day:

                    if int(startTime[11:13]) < hr:
                        errs.append("Start hour too early\n")
                    elif int(startTime[11:13]) == hr:

                        if int(startTime[14:16]) < min:
                            errs.append("Start min too early\n")
        
        if int(startTime[:4]) > int(endTime[:4]): # Invalid year end
            errs.append("End year too early\n")
        elif int(startTime[:4]) == int(endTime[:4]): # This year, check others

            if int(startTime[5:7]) > int(endTime[5:7]):
                errs.append("End month too early\n")
            elif int(startTime[5:7]) == int(endTime[5:7]):

                if int(startTime[8:10]) > int(endTime[8:10]):
                    errs.append("End day too early\n")
                elif int(startTime[8:10]) == int(endTime[8:10]):

                    if int(startTime[11:13]) > int(endTime[11:13]):
                        errs.append("End hour too early\n")
                    elif int(startTime[11:13]) == int(endTime[11:13]):

                        if int(startTime[14:16]) > int(endTime[14:16]):
                            errs.append("End min too early\n")

        if errs:
            return render_template('newGame.html', erNo=len(errs), errs=errs)
        
        # if money < 10000 or money > 1000000:
        #     errs.append("Incorrect money amount\n")
            # check start time has not occured yet
            # check end time exists
            # check end time is not before start time
            # check end time is 

        # settings = db.game.Settings(privacy, money, startTime, endTime)
        # game = db.game.Game.Game(settings, str(time.time()))
        # db.DB.addGame(game)

        # Make sure all inputs are valid

        # Create game in database
        # Attach game to player
        # redirect to game
        game = database.game.Game(name, privacy, money, startTime, endTime)

        invited = request.form.getlist("friend")

        if not app_database.addGame(game):
            errs.append("Game Name taken\n")
            return render_template('newGame.html', erNo=len(errs), errs=errs)
        
        game.addPlayer(app_database.getUser(session["username"]))

        for f in invited:
            game.addPlayer(app_database.getUser(f))
        
        return redirect(url_for('playGame', GAMEID=game.gameID))
    
    return "New game"

# I found "/play/<int:id>" , maybe this could work for the parameter
# I think anything in <> is a url parameter (different than ___=___&___=___)
@app.route("/play", methods=['GET', 'POST'])
@app.route("/play/<GAMEID>", methods=['GET', 'POST'])
def playGame(GAMEID=None):

    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    if request.method == 'GET':
        game = app_database.getGame(GAMEID)
        return render_template('play.html', ID=game.gameID, PLAYERS=game.players) #TODO display more info
    
    elif request.method == 'POST':
        
        if request.form.get("home"):
            return redirect(url_for('homePage'))
    
    return "Play game"

@app.route("/updatingGame/<GAMEID>", methods=['GET', 'POST'])
def updateGame(GAMEID=None):

    if not 'username' in session:
        return redirect(url_for('loginPage'))

    if request.method == 'GET':
        game = app_database.getGame(GAMEID)

        if not game:
            return "Game not found"
        
        return jsonify({"ID":GAMEID, "PLAYERS":game.players})
        # return render_template('play.html', ID=json.dumps(GAMEID), PLAYERS=json.dumps(game.players))
    

@app.route("/view", methods=['GET', 'POST'])
@app.route("/view/<GAMEID>", methods=['GET', 'POST'])
def viewGame(GAMEID=None):

    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    if request.method == 'GET':
        return render_template('viewGame.html', ID=GAMEID)
    
    elif request.method == 'POST':
        
        if request.form.get("home"):
            return redirect(url_for('homePage'))
    
    # Have parameter of which game to view
    
    game = app_database.getGame(GAMEID)
    # just access the game variables directly
    
    # Just view information of it
    return "View game"

@app.route("/profile", methods=['GET', 'POST'])
@app.route("/profile/<USER>", methods=['GET', 'POST'])
def profilePage(USER = None):

    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    if request.method == 'GET':
        current_user = app_database.getUser(session['username'])
        return render_template('profile.html', user=current_user.username, friends=current_user.friends)
    
    elif request.method == 'POST':
        
        if request.form.get("home") == "Home":
            return redirect(url_for('homePage'))
        if request.form.get("friends") == "Friends":
            return redirect(url_for('friendsPage'))
    
    return "Profile screen"

@app.route("/friends", methods=['GET', 'POST'])
def friendsPage():

    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    current_user = app_database.getUser(session['username'])
    friends_list = current_user.friends

    if request.method == 'GET':
        return render_template('friends.html', friends=friends_list)
    
    elif request.method == 'POST':
        
        if request.form.get("home") == "Home":
            return redirect(url_for('homePage'))
        
        print("Before view")
        
        viewFriend = request.form.get("View")
        if viewFriend != None:
            friend = app_database.getUser(viewFriend)
            if friend is not None:
                return render_template('profile.html', user=friend.username, friends=friend.friends)
            # else:
                # error
        
        print("Before add")
        
        if request.form.get("userAction") == "Add Friend":
            print("In add")
            friend_username = request.form.get("friendUsername")
            friend = app_database.getUser(friend_username)
            if friend is None:
            # some kind of error
                pass
            else:
                if friend.username not in friends_list and friend.username != session['username']:
                    current_user.add_friend(friend.username)
                    friends_list = current_user.friends

        print("After add")
        
        return render_template('friends.html', friends=friends_list)
    
    # Use cookie to find user and return the friends
    
    return "Friends page"


@app.route("/settings", methods=['GET', 'POST'])
def settingsPage():

    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    if request.method == 'GET':
        return render_template('settings.html')
    
    elif request.method == 'POST':
        
        if request.form.get("home"):
            return redirect(url_for('homePage'))
    
    # Settings or something maybe
    return "Settings page"

# online = []
recentButtonPress = None
@app.route("/testOnline", methods=['GET', 'POST'])
def testOnline():

    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    global online
    global recentButtonPress

    if session['username'] not in online:
        online.append(session['username'])

    if request.method == 'GET':
        return render_template('testOnline.html', onl=json.dumps(online), rbp=json.dumps(recentButtonPress))

@app.route("/updatingRBP", methods=['POST'])
def updateRBP():
    global recentButtonPress
    recentButtonPress = session['username']
    return {"rbp":recentButtonPress}

@app.route("/updatingOnlineAndRBPdisplay", methods=['POST'])
def updateOnlineAndRBPdisplay():
    global online
    global recentButtonPress
    return {"rbp":recentButtonPress,
            "onl":online}


@app.route("/<randomstring>")
def wrongUrl(randomstring):
    return redirect(url_for('landingRedirect'))


app.run(port = PORT)#, host="0.0.0.0")  # open to all traffic on network