from flask import Flask, render_template, url_for, request
from flask import redirect, jsonify, make_response, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import SingletonThreadPool
from database_setup import Base, Course, CourseItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
#engine = create_engine('sqlite:///catalog.db?check_same_thread=False',
#                       poolclass=SingletonThreadPool)
engine = create_engine('postgresql://catalog:catalogpass@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu App"


'''
    function decorator for non logged users
'''


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        else:
            return func()
    return wrapper


'''
    here function will handle the course JSON data
'''


@app.route('/course/<int:course_id>/JSON')
def courseItemsJSON(course_id):
    course = session.query(Course).filter_by(id=course_id).one_or_none()

    if course is None:
            return render_template('error.html')
    else:
        items = (session.query(CourseItem)
                 .filter_by(course_id=course_id)
                 .join(Course)
                 .all())
        return jsonify(CourseItems=[i.serialize for i in items])


'''
    function return all courses as JSON when route requested
'''


@app.route('/course/JSON')
def courseJSON():
    course = session.query(Course).all()
    return jsonify(Courses=[i.serialize for i in course])


'''
    login function generate a random state every time page refreshed
    and return login page template
'''


@app.route('/login')
def login():
    state = (''
             .join(random.choice(
                                string.ascii_uppercase +
                                string.digits) for x in xrange(32)))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


'''
    Disconnect user based on provider
'''


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']

        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['user_id']
        del login_session['provider']

        del login_session['state']

        flash("You have successfully been logged out.", "success")
        return redirect(url_for('listCourse'))
    else:
        flash("You were not logged in", "warning")
        return redirect(url_for('listCourse'))

'''
    Gathers data from Google Sign In API and places
    it inside a session variable.
'''


# This has been qouted from Udacity Course
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                                 json.dumps('Current user is' +
                                            'already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    try:
        data['name']
    except KeyError:
        data['name'] = data['email']

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'], "info")
    print "done!"
    return output

'''
    create database user from session and return user id
'''


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

'''
    return user information from its id
'''


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

'''
    return user id from its email
'''


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


'''
    disconnect users logged in with Google Signin
'''


# This has been qouted from Udacity Course
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')

    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
                                            'Failed to revoke token' +
                                            'for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return access_token + ' ' + result['status']


'''
    route handler function
'''


@app.route('/')
@app.route('/course')
def listCourse():
    courses = session.query(Course).all()
    itemss = (session.query(CourseItem)
              .order_by(CourseItem.id.desc())
              .join(Course).limit(5)
              .all())
    return render_template('course.html', courses=courses, items=itemss)

'''
    new course function creates a new course into database
'''


@login_required
@app.route('/course/new', methods=['GET', 'POST'])
def newCourse():
    if request.method == 'POST':
        newCourse = Course(name=request.form['name'])
        session.add(newCourse)
        session.commit()
        flash("A New Course Has Been Created", "success")

        return redirect(url_for('listCourse'))
    else:
        return render_template('newcourse.html')

'''
    function to display all items for a specefic course
'''


@app.route('/course/<int:course_id>')
def showCourse(course_id):
    courses = session.query(Course).all()
    coursename = session.query(Course).filter_by(id=course_id).one_or_none()
    items = session.query(CourseItem).filter_by(course_id=course_id).all()

    if coursename is None:
        return render_template('error.html')
    else:
        return render_template('showcourse.html',
                               courses=courses, items=items,
                               coursename=coursename)

'''
    function to display the item information and ability for owner
    to update it or delete it
'''


@app.route('/course/<int:course_id>/<int:item_id>')
def showCourseItem(course_id, item_id):
    item = (session.query(CourseItem)
            .filter_by(id=item_id, course_id=course_id).one_or_none())

    if item is None:
        return render_template('error.html')
    else:
        user = getUserInfo(item.user_id)
        return render_template('showcourseitem.html',
                               course_id=course_id,
                               item=item, user=user)

'''
    function to create a new course item for logged in users only
'''


@login_required
@app.route('/course/<int:course_id>/new', methods=['GET', 'POST'])
def newCourseItem(course_id):
    course = session.query(Course).filter_by(id=course_id).one_or_none()
    if course is None:
        return render_template('error.html')
    else:
        if request.method == 'POST':
            if course is None:
                return render_template('error.html')
            else:
                newCourseItem = CourseItem(name=request.form['name'],
                                           description=request
                                                       .form['description'],
                                           course_id=course_id,
                                           user_id=login_session['user_id'])
                session.add(newCourseItem)
                session.commit()
                flash("A New Course Item Has Been Created", "success")

                return redirect(url_for('showCourse', course_id=course_id))
        else:
            return render_template('newCourseItem.html')

'''
    function to update an item by its owner only
'''


@login_required
@app.route('/course/<int:course_id>/<int:item_id>/update',
           methods=['GET', 'POST'])
def updateCourseItem(course_id, item_id):
    item = (session.query(CourseItem)
            .filter_by(id=item_id, course_id=course_id)
            .one_or_none())
    if item is None:
        return render_template('error.html')

    elif item.user_id != login_session['user_id']:
        flash("Sorry, You Can Only Update Your Item", "danger")
        return redirect(url_for('showCourseItem',
                                course_id=course_id,
                                item_id=item.id))

    else:
        if request.method == 'POST':
            if request.form['name']:
                item.name = request.form['name']
            if request.form['description']:
                item.description = request.form['description']
            session.add(item)
            session.commit()
            return redirect(url_for('showCourseItem',
                                    course_id=item.course_id,
                                    item_id=item.id))
        else:
            return render_template('updateCourseItem.html', item=item)

'''
    function to delete an item by its owner only
'''


@login_required
@app.route('/course/<int:course_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteCourseItem(course_id, item_id):
    item = (session.query(CourseItem)
            .filter_by(id=item_id, course_id=course_id)
            .one_or_none())
    if item is None:
        return render_template('error.html')

    elif item.user_id != login_session['user_id']:
        flash("Sorry, You Can Only Delete Your Item", "danger")
        return redirect(url_for('showCourseItem',
                                course_id=course_id,
                                item_id=item.id))

    else:
        if request.method == 'POST':
            session.delete(item)
            session.commit()
            return redirect(url_for('showCourse', course_id=item.course_id))
        else:
            return render_template('deletecourseitem.html', item=item)


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5000)
