from flask import Flask, render_template, request, Markup, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from waitress import serve
import pickle
import os
import pandas as pd
import datetime
import os
import sqlite3
import pandas
import secrets
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import PolynomialFeatures
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.compose import make_column_selector as selector
import hashlib

app = Flask(__name__, template_folder='templates', static_folder='templates/assets')
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)

#REAL ESTATE SPECIFIC FUNCTIONS########################################################### START
#real estate
def RE_prepare_zipcode(df : pd.DataFrame) -> dict[int:float]:
    #create zipcode conversion table
    zipcode = {}

    #dropnan from prices
    df2 = df.dropna(subset=['Price'])
    #dropnan from zipcode
    df2 = df2.dropna(subset=['zipcode'])

    for z in list(df2['zipcode'].unique()):
        zipcode[z] = df2[df2['zipcode'] == z]['Price'].median()
        
    return zipcode

#real estate
def RE_prepare_type(df : pd.DataFrame) -> dict[str:float]:
    #create type conversion table
    types = {}

    #dropnan from prices
    df2 = df.dropna(subset=['Price'])
    #dropnan from type
    df2 = df2.dropna(subset=['type'])

    for i in df["type"].unique():
        types[i] = df[df['type'] == i]['Price'].mean()

    return types

#real estate
def RE_prepare_tax(df : pd.DataFrame) -> dict[int:float]:
    #create zipcode conversion table
    zipcode = {}

    #dropnan from tax
    df2 = df.dropna(subset=['Taxe'])
    #dropnan from zipcode
    df2 = df2.dropna(subset=['zipcode'])

    for z in list(df2['zipcode'].unique()):
        zipcode[z] = df2[df2['zipcode'] == z]['Taxe'].mean()

    return zipcode

#real estate
def RE_get_name(zipcode : int) -> str:

    if zipcode < 1300:
        return 'BruxellesCapitale'
    elif zipcode < 1500:
        return 'ProvinceduBrabantwallon'
    elif zipcode < 2000:
        return 'ProvinceduBrabantflamand'
    elif zipcode < 3000:
        return 'ProvincedAnvers'
    elif zipcode < 3500:
        return 'ProvinceduBrabantflamand2'
    elif zipcode < 4000:
        return 'ProvincedeLimbourg'
    elif zipcode < 5000:
        return 'ProvincedeLiege'
    elif zipcode < 6000:
        return 'ProvincedeNamur'
    elif zipcode < 6600:
        return 'ProvinceduHainaut1'
    elif zipcode < 7000:
        return 'ProvincedeLuxembourg'
    elif zipcode < 8000:
        return 'ProvinceduHainaut2'
    elif zipcode < 9000:
        return 'ProvincedeFlandreOccidentale'
    elif zipcode < 10000:
        return 'ProvincedeFlandreOrientale'
    else:
        return ""

#real estate
def RE_check(immo : str, zipcode : str, room : str, surface : str) -> str:
    result = ""
    if immo == "":
        result += "<br> Please choose a category <br/>"

    if zipcode == "":
        result += "<br> Please enter a zipcode <br/>"
    else:
        zipcode = int(zipcode)
        if zipcode < 1000 or zipcode > 9999:
            result += "<br> Please enter a plausible zipcode <br/>"

    if room == "":
        result += "<br> Please enter a number of room <br/>"

    else:
        room = int(room)
        if room < 1 or room > 100:
             result += "<br> Please enter a plausible number of room <br/>"


    if surface == "":
        result += "<br> Please enter a living area <br/>"

    else:
        surface = float(surface)
        if surface < 5 or surface > 1000:
            result += "<br> Please enter a plausible living area <br/>"

    return result

#REAL ESTATE SPECIFIC FUNCTIONS############################################################# END

#CHURNING SPECIFIC FUNCTIONS############################################################## START


#CHURNING SPECIFIC FUNCTIONS################################################################ END

#GENERAL APP FUNCTIONS#################################################################### START

def models_loader() -> dict[str : any]:
    #get the all the file name in the model folder 
    models = {} 
    for file in os.listdir('models'):
        if file.endswith(".pickle"):
            name = file[:-7]
            print(name + " loaded")
            models[name] = pickle.load(open(f'models/{file}', 'rb'))

    return models


def menu(level : int) -> str : 

    if level == 0:

        return f"""
        <li><a href="{url_for('home')}">Home</a></li>
        <li><a href="{url_for('login')}">Log In</a></li>
        <li><a href="{url_for('sign_up')}">Sign Up</a></li>
        """
        
    if level == 1:

        return f"""
        <li><a href="{url_for('home')}">Home</a></li>
        <li><a href="{url_for('profile')}">My profile</a></li>
        <li><a href="{url_for('my_portfolio')}">My portfolio</a></li>
		<li><a href="{url_for('explorator')}">stocks explorator</a></li>
		<li><a href="{url_for('real_estate')}">Real estate</a></li>
        <li><a href="{url_for('logout')}">Log out</a></li>      
        """
    
    if level == 2:

        return f"""
        <li><a href="{url_for('home')}">Home</a></li>
        <li><a href="{url_for('profile')}">My profile</a></li>
        <li><a href="{url_for('my_portfolio')}">My portfolio</a></li>
		<li><a href="{url_for('admin')}">admin panel</a></li>
		<li><a href="{url_for('churn')}">churn predictor</a></li>
        <li><a href="{url_for('explorator')}">stocks explorator</a></li>
		<li><a href="{url_for('real_estate')}">Real estate</a></li>
        <li><a href="{url_for('logout')}">Log out</a></li>      
        """
    
    if level == 3:

        return f"""
        <li><a href="{url_for('home')}">Home</a></li>
        <li><a href="{url_for('profile')}">My profile</a></li>
        <li><a href="{url_for('add_to_db')}">Add my files</a></li>
        <li><a href="{url_for('my_portfolio')}">My portfolio</a></li>
		<li><a href="{url_for('admin')}">admin panel</a></li>
		<li><a href="{url_for('churn')}">churn predictor</a></li>
        <li><a href="{url_for('explorator')}">stocks explorator</a></li>
		<li><a href="{url_for('real_estate')}">Real estate</a></li>
        <li><a href="{url_for('logout')}">Log out</a></li>      
        """

    return "Error attribution level"

def buttons(level : int, username : str) -> str:
    if level == 0:

        return f"""

        <section>
        <h3 class="major">Where do you want to go?</h3>

        <ul class="actions fit">
			<li><a href="{url_for('login')}" class="button fit icon solid fa-user">Login</a></li>
			<li><a href="{url_for('sign_up')}" class="button fit icon solid fa-user-plus">Sign up</a></li>
		</ul>        
        </section>

        """

    if level == 1:

        return f"""

        <section>
        <h3 class="major">Where do you want to go {username}?</h3>

        <ul class="actions fit">
			<li><a href="{url_for('profile')}" class="button fit icon solid fa-id-card">My profile</a></li>
			<li><a href="{url_for('explorator')}" class="button fit icon solid fa-search">Stocks explorator</a></li>
		</ul>
		<ul class="actions fit">
			<li><a href="{url_for('real_estate')}" class="button fit icon solid fa-city">Real estate</a></li>
			<li><a href="{url_for('my_portfolio')}" class="button fit icon solid fa-table">My portfolio</a></li>
		</ul>
		<ul class="actions fit">
			<li><a href="{url_for('logout')}" class="button fit icon solid fa-user-slash">Logout</a></li>
		</ul>       
        </section>

        """

    if level == 2:

        return f"""

        <section>
        <h3 class="major">Where do you want to go {username}?</h3>

        <ul class="actions fit">
			<li><a href="{url_for('profile')}" class="button fit icon solid fa-id-card">My profile</a></li>
			<li><a href="{url_for('explorator')}" class="button fit icon solid fa-search">Stocks explorator</a></li>
		</ul>
        <ul class="actions fit">
			<li><a href="{url_for('admin')}" class="button fit icon solid fa-chess-queen">Admin panel</a></li>
			<li><a href="{url_for('churn')}" class="button fit icon solid fa-people-arrows">Churn predictor</a></li>
		</ul>
		<ul class="actions fit">
			<li><a href="{url_for('real_estate')}" class="button fit icon solid fa-city">Real estate</a></li>
			<li><a href="{url_for('my_portfolio')}" class="button fit icon solid fa-table">My portfolio</a></li>
		</ul>
		<ul class="actions fit">
			<li><a href="{url_for('logout')}" class="button fit icon solid fa-user-slash">Logout</a></li>
		</ul>       
        </section>

        """
    
    if level == 3:

        return f"""

        <section>
        <h3 class="major">Where do you want to go {username}?</h3>

        <ul class="actions fit">
			<li><a href="{url_for('profile')}" class="button fit icon solid fa-id-card">My profile</a></li>
			<li><a href="{url_for('explorator')}" class="button fit icon solid fa-search">Stocks explorator</a></li>
		</ul>
        <ul class="actions fit">
			<li><a href="{url_for('admin')}" class="button fit icon solid fa-chess-queen">Admin panel</a></li>
			<li><a href="{url_for('churn')}" class="button fit icon solid fa-people-arrows">Churn predictor</a></li>
		</ul>
		<ul class="actions fit">
			<li><a href="{url_for('real_estate')}" class="button fit icon solid fa-city">Real estate</a></li>
			<li><a href="{url_for('my_portfolio')}" class="button fit icon solid fa-table">My portfolio</a></li>
		</ul>
		<ul class="actions fit">
			<li><a href="{url_for('add_to_db')}" class="button fit icon solid fa-plus">Add my file</a></li>
            <li><a href="{url_for('logout')}" class="button fit icon solid fa-user-slash">Logout</a></li>
		</ul>       
        </section>

        """

    return "Error attribution level"

def add_user(username : str, password : str, level : int) -> None:
    """Add a user to the database"""
    try:
        with sqlite3.connect("databases/users.db") as conn:
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE users (username TEXT, password TEXT, level INTEGER)')
            conn.commit()
    except:
        print("Table already exists")
    with sqlite3.connect("databases/users.db") as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users VALUES (?, ?, ?)', (username, password, level))
        conn.commit()


def check_user(username : str, password : str) -> bool:
    """Check if the user exists in the database"""
    with sqlite3.connect("databases/users.db") as conn:
        
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username))
        if cursor.fetchone() is None:
            return False
        else:
            return True











								
							
@app.route('/')
def home():

    try:

        connected = session['connected'] 
        username = session['username']

    except: 

        session['connected'] : int = 0
        session['username'] : str = "Not connected"
        connected = session['connected'] 
        username = session['username']

    message = "Welcome! You are not connected."
    
    if connected == 1:
        message = f"Welcome {username}!"
    
    if connected == 2:
        message = f"Welcome {username}! You have employee privileges."
    
    if connected == 3:
        message = f"Welcome {username}! You have admin privileges."

    
    return render_template('index.html', 
                           Connected = username, 
                           menu = Markup(menu(connected)),
                           buttons = Markup(buttons(connected, username)),
                           message = message
                          )



@app.route('/')
def my_portfolio():
    return home()

@app.route('/')
def admin():
    return home()

@app.route('/')
def churn():
    return home()

@app.route('/')
def explorator():
    return home()

@app.route('/')
def real_estate():
    return home()

@app.route('/')
def add_to_db():
    return home()

@app.route('/')
def profile():
    return home()

@app.route('/')
def login():
    return home()


@app.route('/signup', methods = ['GET', 'POST'])
def sign_up():

    try:
        connected = session['connected'] 
        username = session['username']
    except:
        return home()
    
    if request.method == 'POST':
        
        if request.form['password'] != request.form['password2']:
            return render_template('signup.html', 
                                   wrong = "Passwords don't match", 
                                   Connected = username, 
                                   menu = Markup(menu(connected)))
        
        try:
            if check_user(request.form['username']):
                return render_template('signup.html', 
                                   wrong = "User already exists", 
                                   Connected = username, 
                                   menu = Markup(menu(connected)))
        
        except:
            print("1")
        
        try:

            attr_level = 1
            if request.form['attr_level'] == "Employee":
                attr_level = 2
            if request.form['attr_level'] == "Admin":
                attr_level = 3

        except:
            print("2")
        
                

        session['connected'] = attr_level
        session['username']= request.form['username']

        try:
            add_user(request.form['username'], request.form['password'], attr_level)
        except:
            print("3")
        add_user(request.form['username'], request.form['password'], attr_level)
        return home()


    if session['connected'] == 0:
        return render_template('signup.html', 
                               Connected = username, 
                               menu = Markup(menu(connected)))
    
    return home()


@app.route('/logout')
def logout():

    try:
        connected = session['connected'] 
        username = session['username']
    except:
        return home()

    if session['connected'] == 0:
        return home()
    
    session['connected'] = 0
    session['username']= "Not connected"
    return render_template('logout.html')


#GENERAL APP FUNCTIONS###################################################################### END





#data for real estate prediction
data_RE : pd.DataFrame = pd.read_csv('data/data_for_regression.csv')
#prepare the data
zipcode_converter : dict[int:float] = RE_prepare_zipcode(data_RE)
tax_converter : dict[int:float] = RE_prepare_tax(data_RE)
type_converter : dict[str:float] = RE_prepare_type(data_RE)


#load machine learning models
# for churn prediction 
# and real estate prediction
models : dict[str:any] = models_loader()




app.run(debug=False)