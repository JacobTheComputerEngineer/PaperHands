from flask import Flask, request, redirect, url_for

app = Flask(__name__)

PORT = 5000

# FOR ALL PAGES
# If user is not logged in, route to loginPage

# It looks like we may need to do some HTML as well
# We can return render_template(html file, var=thing, var=thing)
# We also may need to do lots of @app.route("/PATH",methods = ['POST', 'GET'])
# https://www.tutorialspoint.com/flask/flask_quick_guide.htm
# https://pythonbasics.org/flask-cookies/

@app.route("/")
def landingRedirect():

    # Check cookies for login maybe?

    # If user not logged in
    return redirect(url_for('loginPage'))

    # Else user logged in
    return redirect(url_for('home'))

@app.route("/login")
def loginPage():
    # login logic here

    # Add button to go to createAccount
    # Need to sanitize user inputs
    # Need to check inputs from database of logins
    # If fail, clear entries and display failed somehow
    # If pass
        # return redirect(url_for('home'))
    return "Log in here"

@app.route("/createAccount")
def createNewUser():
    # Need to sanitize user inputs
    # Check username is open (and matches other reqs)
    # Added user inputs to database for successful creation
    # Clear entries and display failed if failed
    # Upon success, redirect to home with login cookie
    return "Create account here"

@app.route("/home")
def homePage():
    # Buttons to redirect to different pages
        # Games
        # Profile
            # with parameter for user
        # Friends
        # Settings maybe
    # Log out button
    return "Home page"

@app.route("/games")
def gamesPage():
    # Buttons to
        # Join game
        # View current games
        # View Old games
        # Make new games
        # Back to home
    return "Games screen"

@app.route("/joingame")
def joinGame():
    # View public games
    # View friends games
    # Join button
        # Attach game to user
        # Move to game
    return "Join game"

@app.route("/activegames")
def currentGames():
    # Display list of active games user is part of
    # Button to move to any game page
    # Back button
    return "Active games"

@app.route("/oldgames")
def oldGames():
    # Display list of any completed games user was part of
    # Button to view any of the pages
    # Back button
    return "Old games"

@app.route("/newgame")
def createGame():
    # Settings for the game
        # Public/private
        # Money
        # Yadayadayada
        # Invite friends (send email or in-game message?)
    # Attach user to game
    # Move to game
    # Cancel button
        # Move user back to games page
    return "New game"

# I found "/play/<int:id>" , maybe this could work for the parameter
# I think anything in <> is a url parameter (different than ___=___&___=___)
@app.route("/play")
def playGame():
    # Have parameter of which game to play
    # Update contents every second
        # This will be tricky to figure out

    return "Play game"

@app.route("/view")
def viewGame():
    # Have parameter of which game to view
    # Just view information of it
    return "View game"

@app.route("/profile")
def profilePage():
    # Use parameter to find user
    # Display profile info for that user
    # Home button
    # Friends button
    return "Profile screen"

@app.route("/friends")
def friendsPage():
    # Use cookie to find user and return the friends
    # Add friend textbox/button
    # View friend profile
        # route to profile with a parameter
    return "Friends page"

@app.route("/settings")
def settingsPage():
    # Settings or something maybe
    return "Settings page"

app.run(port = PORT)#, host="0.0.0.0")  # open to all traffic on network