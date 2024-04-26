# Importing the frameworks

from flask import *
from datetime import datetime
import database

user_details = {}
session = {}
page = {}

# Initialise the application
app = Flask(__name__)
app.secret_key = 'aab12124d346928d14710610f'


#####################################################
##  INDEX
#####################################################

@app.route('/')
def index():
    # Check if the user is logged in
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    page['title'] = 'Fine Food Kitchen'
    
    return redirect(url_for('list_menuitem'))

    #return render_template('index.html', session=session, page=page, user=user_details)

#####################################################
##  LOGIN
#####################################################

@app.route('/login', methods=['POST', 'GET'])
def login():
    # Check if they are submitting details, or they are just logging in
    if (request.method == 'POST'):
        # submitting details
        login_return_data = check_login(request.form['id'], request.form['password'])

        # If they have incorrect details
        if login_return_data is None:
            page['bar'] = False
            flash("Incorrect login info, please try again.")
            return redirect(url_for('login'))

        # Log them in
        page['bar'] = True
        welcomestr = 'Welcome back, ' + login_return_data['firstName'] + ' ' + login_return_data['lastName']
        flash(welcomestr)
        session['logged_in'] = True

        # Store the user details
        global user_details
        user_details = login_return_data
        return redirect(url_for('index'))

    elif (request.method == 'GET'):
        return(render_template('login.html', page=page))

#####################################################
##  LOGOUT
#####################################################

@app.route('/logout')
def logout():
    session['logged_in'] = False
    page['bar'] = True
    flash('You have been logged out. See you soon!')
    return redirect(url_for('index'))

#####################################################
##  List Menu Item
#####################################################

@app.route('/list_menuitem', methods=['POST', 'GET'])
def list_menuitem():
    # Check if user is logged in
    if ('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    # User is just viewing the page
    if (request.method == 'GET'):
        # First check if specific menu item
        menuitem_list = database.findMenuItemsByStaff(user_details['staffID'])
        if (menuitem_list is None):
            menuitem_list = []
            flash("There are no menu items in the system for " + user_details['firstName'] + " " + user_details['lastName'])
            page['bar'] = False
        return render_template('menuitem_list.html', menuitem=menuitem_list, session=session, page=page)

    # Otherwise try to get from the database
    elif (request.method == 'POST'):
        search_term = request.form['search']
        if (search_term == ''):
            menuitem_list_find = database.findMenuItemsByStaff(user_details['staffID'])
        else:    
            menuitem_list_find = database.findMenuItemsByCriteria(search_term)
        if (menuitem_list_find is None):
            menuitem_list_find = []
            flash("Searching \'{}\' does not return any result".format(request.form['search']))
            page['bar'] = False
        return render_template('menuitem_list.html', menuitem=menuitem_list_find, session=session, page=page)

#####################################################
##  Add Menu Item
#####################################################

@app.route('/new_menuitem' , methods=['GET', 'POST'])
def new_menuitem():
    # Check if the user is logged in
    if ('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    # If we're just looking at the 'new menu item' page
    if(request.method == 'GET'):
        times = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
        return render_template('new_menuitem.html', user=user_details, times=times, session=session, page=page)

	# If we're adding a new menu item
    success = database.addMenuItem(request.form['name'],
                              request.form['description'],
                              request.form['categoryone'],
                              request.form['categorytwo'],
                              request.form['categorythree'],
                              request.form['coffeetype'],
                              request.form['milkkind'],
                              request.form['price'])
    if(success == True):
        page['bar'] = True
        flash("Menu item added!")
        return(redirect(url_for('index')))
    else:
        page['bar'] = False
        flash("There was an error adding a new menu item")
        return(redirect(url_for('new_menuitem')))

#####################################################
## Update Menu Item
#####################################################
@app.route('/update_menuitem', methods=['GET', 'POST'])
def update_menuitem():
    # Check if the user is logged in
    if ('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    # If we're just looking at the 'update menu item' page
    if (request.method == 'GET'):
        # categories
        categorylen = len(request.args.get('category').split("|"))
        if (categorylen == 1):
            categoryone = request.args.get('category').split("|")[0]
            categorytwo = ''
            categorythree = ''
        elif (categorylen == 2):
            categoryone = request.args.get('category').split("|")[0]
            categorytwo = request.args.get('category').split("|")[1]
            categorythree = ''
        elif (categorylen == 3):
            categoryone = request.args.get('category').split("|")[0]
            categorytwo = request.args.get('category').split("|")[1]
            categorythree = request.args.get('category').split("|")[2]
        else:
            categoryone = ''
            categorytwo = ''
            categorythree = ''

        # coffee option
        optionlen = len(request.args.get('coffeeoption').split(" - "))
        if (optionlen == 1):
            coffeetype = request.args.get('coffeeoption').split(" - ")[0]
            milkkind = ''
        elif (optionlen == 2):
            coffeetype = request.args.get('coffeeoption').split(" - ")[0]
            milkkind = request.args.get('coffeeoption').split(" - ")[1]
        else:
            coffeetype = ''
            milkkind = ''

        # review date
        datelen = len(request.args.get('reviewdate'))
        if (datelen > 0):
            reviewdate = datetime.strptime(request.args.get('reviewdate'), '%d-%m-%Y').date()
        else:
            reviewdate = ''

        # Get the menu item
        menuitem = {
            'menuitem_id': request.args.get('menuitem_id'),
            'name': request.args.get('name'),
            'description': request.args.get('description'),
            'categoryone': categoryone,
            'categorytwo': categorytwo,
            'categorythree': categorythree,
            'coffeetype': coffeetype,
            'milkkind': milkkind,
            'price': request.args.get('price'),
            'reviewdate': reviewdate,
            'reviewer': request.args.get('reviewer'),
        }

        # If there is no menu item
        if menuitem['menuitem_id'] is None:
            menuitem = []
		    # Do not allow viewing if there is no menu item to update
            page['bar'] = False
            flash("You do not have access to update that record!")
            return(redirect(url_for('index')))

	    # Otherwise, if menu item details can be retrieved
        times = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
        return render_template('update_menuitem.html', menuItemInfo=menuitem, user=user_details, times=times, session=session, page=page)

    # If we're updating menu item (a POST)
    # Check review date
    revdate = request.form['reviewdate']
    if (revdate == ''):
        revdate = None
    success = database.updateMenuItem(request.form['menuitem_id'],
                                request.form['name'],
                                request.form['description'],
                                request.form['categoryone'],
                                request.form['categorytwo'],
                                request.form['categorythree'],
                                request.form['coffeetype'],
                                request.form['milkkind'],
                                request.form['price'],
                                revdate,
                                request.form['reviewer'])

    if (success == True):
        page['bar'] = True
        flash("Menu item record updated!")
        return(redirect(url_for('index')))
    else:
        page['bar'] = False
        flash("There was an error updating the menu item")
        return(redirect(url_for('index')))

def get_menuitem(menuitem_id, staffID):
    for menuitem in database.findMenuItemsByStaff(staffID):
        if menuitem['menuitem_id'] == menuitem_id:
            return menuitem
    return None

def check_login(staffID, password):
    userInfo = database.checkStaffLogin(staffID, password)

    if userInfo is None:
        return None
    else:
        tuples = {
            'staffID': userInfo[0],
            'password': userInfo[1],
            'firstName': userInfo[2],
            'lastName': userInfo[3],
            'age': userInfo[4],
            'salary': userInfo[5]
        }
        return tuples
