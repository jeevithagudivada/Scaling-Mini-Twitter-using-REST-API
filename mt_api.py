# -*- coding: utf-8 -*-
"""
    MiniTwit
    ~~~~~~~~

    A microblogging application written with Flask and sqlite3.

    :copyright: © 2010 by the Pallets team.
    :license: BSD, see LICENSE for more details.
"""

import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, jsonify, json, Response
from werkzeug import check_password_hash, generate_password_hash



# configuration
DATABASE = '/tmp/minitwit.db'
PER_PAGE = 30
DEBUG = True
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

# create our little application :)
app = Flask('minitwit')
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database in the Linix system.')

def populate_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('population.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('populatedb')
def populatedb_command():
    """Creates the database tables."""
    populate_db()
    print('Initialized the database.')

def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = query_db('select user_id from user where username = ?',
                  [username], one=True)
    return rv[0] if rv else None

#get password
def get_password(username):
    """Convenience method to look up the id for a username."""
    rv = query_db('select pw_hash from user where username = ?',
                  [username], one=True)
    return rv[0] if rv else None


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


# 1. PUBLIC -- Good !! for public page
@app.route('/app/public',methods=['GET'])
def public_timeline():
    #init_db()
    #populate_db()
    s = query_db('select message.*, user.username,user.email from message, user where message.author_id = user.user_id order by message.pub_date desc limit 30;')
    #s = query_db('select * from user;')
    return (jsonify([dict(r) for r in s]),200)

# 2.LOGIN -- good!! successfully working
@app.route('/app/login',methods=['GET','POST'])
def login():
    #init_db()
    #populate_db()
    content = request.get_json()
    name = content['username']
    pword = content['password']
    valid_user = get_user_id(name)
    if valid_user is None:
            return (Response(json.dumps({
            'message' : 'Invalid username'
            }), mimetype='application/json'),400)
    #passw=query_db('select * from user where username = ? and pw_hash = ?',[name,check_password_hash(pword)], )
    pwordc=get_password(name)
    if not check_password_hash(pwordc,pword):
            return (Response(json.dumps({
            'message' : 'Invalid Password'
            }), mimetype='application/json'),400)
    else:
        #res = json.stringify({"message" : "Loogedd"})
        #return (jsonify("Successfully logged in"),200)
        return (Response(json.dumps({
        'message' : 'Successfully logged in'
        }), mimetype='application/json'),200)

# 3.Register -- good!! succeeslly working for registering user
@app.route('/app/register',methods=['GET','POST'])
def register():
    #init_db()
    #populate_db()
    content = request.get_json()
    name = content['username']
    email = content['email_id']
    pword1 = content['password1']
    pword2 = content['password2']
    if name is None:
        return (Response(json.dumps({
        'message' : 'Please enter user name'
        }), mimetype='application/json'),400)
    if len(pword1) < 8:
        return (Response(json.dumps({
        'message' : 'Password should be more than 8 charactes'
        }), mimetype='application/json'),400)
    if pword1 != pword2:
        #return jsonify("Please check the password. Mismatch of passwords")
        return (Response(json.dumps({
        'message' : 'Please check the password. Mismatch of passwords'
        }), mimetype='application/json'),400)
    ex_mail_id =  query_db('select * from user where email = ?',[email])
    #return jsonify(ex_mail_id)
    if ex_mail_id:
        #return jsonify("This Email_id has been already registered try new one")
        return (Response(json.dumps({
        'message' : 'This Email_id has been already registered try new one'
        }), mimetype='application/json'),400)
    ex_name =  query_db('select * from user where username = ?',[name])
    #return jsonify(ex_mail_id)
    if ex_name:
        #return jsonify("This Email_id has been already registered try new one")
        return (Response(json.dumps({
        'message' : 'This User name has been already registered try new one'
        }), mimetype='application/json'),400)
    else:
        db = get_db()
        db.execute('insert into user (username, email, pw_hash) values (?, ?, ?)',[name,email,generate_password_hash(pword1)])
        db.commit()
        #return (jsonify("You have been successfully registered"),201)
        return (Response(json.dumps({
        'message' : 'You have been successfully registered'
        }), mimetype='application/json'),201)
    #All_users = query_db('select * from user')
    #return jsonify([dict(r) for r in All_users])

#4.USER TIMELINE good!! returns all mesgs of the loggeduser's following users
@app.route('/app/<username>/timeline',methods=['GET'])
def user_timeline(username):
    #init_db()
    #populate_db()
    Loged_user = query_db('select * from user where username = ?',[username], one=True)
    if Loged_user is None:
        abort(404)
        # should display all the posts whom he is following
    user_id = query_db('select user_id from user where username = ?',[username])
    #return jsonify([dict(r) for r in user_id])
    post = query_db('select message.*, user.* from message, user, follower where user.user_id = message.author_id and user.user_id in (select whom_id from follower where who_id = ?) group by user_id order by message.pub_date',[get_user_id(username)])
    return (jsonify([dict(r) for r in post]),200)

# 5.DISPLAYING ALL POSTS -- good !! displays all loggeduser's posts
@app.route('/app/<username>/posts',methods=['GET'])
def user_posts(username):
    #init_db()
    #populate_db()
    Loged_user = get_user_id(username)
    if Loged_user is None:
        abort(404)
    else:
        post = query_db('select message.* from message where author_id = ?',[get_user_id(username)])
        if not post:
            #return (jsonify("No posts for this user"),204) #content not found
            return (Response(json.dumps({
            'message' : 'you do not have any posts'
            }), mimetype='application/json'),200)
        else:
            return (jsonify([dict(r) for r in post]),200)

#6. USER FOLLOWINGS -- good !! displays all list of user that current user is following
@app.route('/app/<username>/following',methods=['GET'])
def user_following(username):
    #init_db()
    #populate_db()
    Loged_user = get_user_id(username)
    if Loged_user is None:
        abort(404)
    else:
        post = query_db('select user.username, user.email from follower, user where follower.whom_id = user.user_id and follower.who_id = ?',[get_user_id(username)])
        #post = query_db('select user.username, user.email from follower, user where follower.whom_id = user.user_id and follower.who_id = 1')
        if not post:
            return (Response(json.dumps({
            'message' : 'you are not following any one'
            }), mimetype='application/json'),200)
        else:
            return (jsonify([dict(r) for r in post]),200)

#7. PARTICULAR  USER'S POSTS --good !! Return of a particular that the logged user is followings
@app.route('/app/<username>/<guestuser>/posts',methods=['GET'])
def user_following_messages(username,guestuser):
    #init_db()
    #populate_db()
    Loged_user = get_user_id(username)
    if Loged_user is None:
        abort(404)
    Loged_user = get_user_id(guestuser)
    if Loged_user is None:
        abort(404)
    follow = query_db('select * from follower where who_id = ? and whom_id = ?',[get_user_id(username),get_user_id(guestuser)])
    if not follow:
        abort(401)
    else:
        post = query_db('select message.* from message where author_id = ?',[get_user_id(guestuser)])
        return jsonify([dict(r) for r in post])

#8. FOLLOW --good!! user following guest user
@app.route('/app/<username>/<guestuser>/follow',methods=['GET','POST'])
def user_follow(username,guestuser):
    #init_db()
    #populate_db()
    Loged_user = get_user_id(username)
    if Loged_user is None:
        abort(404)
    Loged_user = get_user_id(guestuser)
    if Loged_user is None:
        abort(404)
    follow = query_db('select * from follower where who_id = ? and whom_id = ?',[get_user_id(username),get_user_id(guestuser)])
    if not follow:
        db = get_db()
        db.execute('INSERT into follower values(?,?)',[get_user_id(username),get_user_id(guestuser)])
        db.commit()
        #return (jsonify("Successfully following !!"), 200)
        return (Response(json.dumps({
        'message' : 'Successfully followings !!'
        }), mimetype='application/json'),200)
    else:
        #return (jsonify("You are already following!!"), 200)
        return (Response(json.dumps({
        'message' : 'You are already followings !!'
        }), mimetype='application/json'),200)
    #post = query_db('select * from follower where who_id = ? and whom_id = ?',[get_user_id(username),get_user_id(guestuser)])
    #return (jsonify([dict(r) for r in post]),200)

#9. UNFOLLOW --good !! user unfollowing guest user
@app.route('/app/<username>/<guestuser>/unfollow',methods=['GET','POST'])
def user_uhfollow(username,guestuser):
    #init_db()
    #populate_db()
    Loged_user = get_user_id(username)
    if Loged_user is None:
        abort(404)
    Loged_user = get_user_id(guestuser)
    if Loged_user is None:
        abort(404)
    follow = query_db('select * from follower where who_id = ? and whom_id = ?',[get_user_id(username),get_user_id(guestuser)])
    if follow:
        db = get_db()
        db.execute('delete from follower where who_id = ? and whom_id =?',[get_user_id(username),get_user_id(guestuser)])
        db.commit()
        #return (jsonify("Unfolloing is successfully completed"),200)
        return (Response(json.dumps({
        'message' : 'Unfollowings is succeeslly completed!!'
        }), mimetype='application/json'),200)
    else:
        #return (jsonify("You are not Folloing the user"), 203)
        return (Response(json.dumps({
        'message' : 'you are not following the user!!'
        }), mimetype='application/json'),203)


#10.ADDING POSTS--  good !! adds messages to by the user and update the message table
@app.route('/app/<username>/add_message', methods=['POST'])
def add_message(username):
        #init_db()
        #populate_db()
        Loged_user = query_db('select * from user where username = ?',[username], one=True)
        if Loged_user is None:
            abort(404)
        #text=request.json.get('message_txt')
        content = request.get_json()
        mtext = content['message_txt']
        db = get_db()
        db.execute('INSERT into message (author_id,text, pub_date) values(?,?,?)',(get_user_id(username),mtext,datetime.today()))
        db.commit()
        All_mesgs = query_db('select * from message where author_id = ?',[get_user_id(username)])
        return (jsonify([dict(r) for r in All_mesgs]),200)
        #return jsonify("Hey message added")

#11. LOGOUT -- good!! successfully logout
@app.route('/app/<username>/logout', methods=['GET'])
def userlogout(username):
    return (Response(json.dumps({
    'message' : 'Successfully loggedout'
    }), mimetype='application/json'),200)


app.jinja_env.filters['datetimeformat'] = format_datetime
