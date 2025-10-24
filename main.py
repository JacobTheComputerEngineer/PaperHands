from flask import Flask, request, redirect, url_for, render_template, session
import json
from database import database as db
import time # easy gameID

app = Flask(__name__)

PORT = 5000

# It looks like we may need to do some HTML as well
# We can return render_template(html file, var=thing, var=thing)
# https://www.tutorialspoint.com/flask/flask_quick_guide.htm
# https://pythonbasics.org/flask-cookies/
# https://flask.palletsprojects.com/en/stable/quickstart/

app.secret_key = b'SECRETKEYEXAMPLE' # quickstart says we need it, may be under the hood stuff

@app.route("/")
def landingRedirect():

    # If user not logged in
    if 'username' in session:
        return redirect(url_for('homePage'))

    # Else user logged in
    return redirect(url_for('loginPage'))

@app.route("/login", methods=['GET', 'POST'])
def loginPage():

    # Logged in already
    if 'username' in session:
        return redirect(url_for('homePage'))
    
    # Display page
    if request.method == 'GET':
        return render_template('login.html')
    
    elif request.method == 'POST':
        # SANITIZE USER INPUTS
        un = request.form.get("Username")
        pw = request.form.get("Password")
        session['username'] = un
        print(un)
        print(pw)

        # Check database

        # If in database
        return redirect(url_for('homePage'))
    
        # If not in database
        return redirect(url_for('loginPage'))

@app.route("/createAccount", methods=['GET', 'POST'])
def createNewUser():

    # Logged in already
    if 'username' in session:
        return redirect(url_for('homePage'))
    
    if request.method == 'GET':
        return render_template('login.html')
    
    elif request.method == 'POST':
        # SANITIZE USER INPUTS
        un = request.form.get("Username")
        pw = request.form.get("Password")
        cw = request.form.get("Confirm Password")
        fk = request.form.get("Finnhub Key")
        session['username'] = un

        # If
        #   Username is new
        #   pw == cw
        #   fk is a properly working key
        return redirect(url_for('homePage'))
    
        # Else
        return redirect(url_for('createNewUser'))

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
        return render_template('joinGame.html')
    
    elif request.method == 'POST':
        
        if request.form.get("home"):
            return redirect(url_for('homePage'))
    
    # View public games
    # View friends games
    # Join button
        # Attach game to user
        # Move to game

    # THIS WILL BE VERY HEAVY

    # For every game available for player to join
    #   Display it 
    #   Be able to click on it
    #       Add game to player
    #       Move to playGame

    return "Join game"

@app.route("/activegames", methods=['GET', 'POST'])
def currentGames():

    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    if request.method == 'GET':
        return render_template('activeGames.html')
    
    elif request.method == 'POST':
        
        if request.form.get("home"):
            return redirect(url_for('homePage'))
    
    # Display list of active games user is part of
    # Button to move to any game page
    # Back button

    # THIS WILL ALSO BE HEAVY

    # For every not completed game attached to the player
    #   Display it 
    #   Be able to click on it
    #       Move to playGame

    return "Active games"

@app.route("/oldgames", methods=['GET', 'POST'])
def oldGames():

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
        return render_template('newGame.html')
    
    elif request.method == 'POST':

        if request.form.get("back"):
            return redirect(url_for('gamesPage'))

        # SANITIZE USER INPUTS
        privacy = request.form.get("privacyStatus")
        money = request.form.get("moneyAmount")
        startTime = request.form.get("startTime")
        endTime = request.form.get("endTime")

        settings = db.game.Settings(privacy, money, startTime, endTime)
        game = db.game.Game.Game(settings, str(time.time()))
        db.DB.addGame(game)

        # Make sure all inputs are valid

        # Create game in database
        # Attach game to player
        # redirect to game
        
        return redirect(url_for('homePage'))
    
    return "New game"

# I found "/play/<int:id>" , maybe this could work for the parameter
# I think anything in <> is a url parameter (different than ___=___&___=___)
@app.route("/play", methods=['GET', 'POST'])
@app.route("/play/<GAMEID>", methods=['GET', 'POST'])
def playGame(GAMEID=None):

    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    if request.method == 'GET':
        return render_template('play.html', ID=GAMEID)
    
    elif request.method == 'POST':
        
        if request.form.get("home"):
            return redirect(url_for('homePage'))
    
    # Have parameter of which game to play
    # Update contents every second
        # This will be tricky to figure out

    # HEAVIEST FUNCTION
    # WARNING THIS THING WILL BE HUGE
    # WER'RE GONNA NEED A BIGGER BOAT

    return "Play game"

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
    # Just view information of it
    return "View game"

@app.route("/profile", methods=['GET', 'POST'])
@app.route("/profile/<USER>", methods=['GET', 'POST'])
def profilePage(USER=None):

    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    if request.method == 'GET':
        return render_template('profile.html', user=USER)
    
    elif request.method == 'POST':
        
        if request.form.get("home"):
            return redirect(url_for('homePage'))
    
    # Use parameter to find user
    # Display profile info for that user
    # Home button
    # Friends button
    return "Profile screen"

@app.route("/friends", methods=['GET', 'POST'])
def friendsPage():

    if not 'username' in session:
        return redirect(url_for('loginPage'))
    
    if request.method == 'GET':
        return render_template('friends.html')
    
    elif request.method == 'POST':
        
        if request.form.get("home"):
            return redirect(url_for('homePage'))
    
    # Use cookie to find user and return the friends
    # Add friend textbox/button
    # View friend profile
        # route to profile with a parameter
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

online = []
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