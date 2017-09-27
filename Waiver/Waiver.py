import os
import sqlite3
from flask import Flask,request,session,g,redirect,url_for,abort,render_template,flash

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path,'Waiver.db'),
    SECRET_KEY='och3weifeiVae4iuKeecaeleeF1vee6vei7u',
    USERNAME='trailsroc',
    PASSWORD='stripe.serious.come.duck.7'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database"""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_waiver():
    if not hasattr(g,'waiverText'):
        with app.open_resource('TrailsRoc  Group Run Waiver.docx.txt','r') as f:
            g.waiverText = f.read()
    return g.waiverText

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if not hasattr(g,'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.route('/')
def show_waiver():
    db = get_db()
    cur = db.execute('select id,name from activities where activeP==1')
    entries = cur.fetchall()
    return render_template('show_waiver.html',waiver=get_waiver(),activities=entries)

@app.route('/sign',methods=['POST'])
def sign_waiver():
    return render_template('enter_signature.html')

@app.route('/commit',methods=['POST'])
def commit_waiver():
    from datetime import datetime

    try:
        filename = os.path.join(app.config['UPLOAD_FOLDER'],datetime.now().strftime('%Y%m%d-%H%M%S%f.png'))
        flash(filename)
        with open(filename,'w') as out:
            out.write(request.form['signature'])
    except:
        flash('Failed to record signature')
        return redirect(url_for('sign_waiver'))
    # I need the data at this point to create the PDF
    flash('New entry was successfully posted')
    return redirect(url_for('show_waiver'))

@app.route('/review')
def review_waivers():
    return render_template('waiver_data.html')
#@app.route('/add',methods=['POST'])
#def add_entry():
#    if not session.get('logged_in'):
#        abort(401)
#    db = get_db()
#    db.execute('insert into entries (title, text) values (?,?)',
#    [request.form['title'], request.form['text']])
#    db.commit()
#    flash('New entry was successfully posted')
#    return redirect(url_for('show_entries'))

#@app.route('/login',methods=['GET','POST'])
#def login():
#    error = None
#    if request.method == 'POST':
#        if request.form['username'] != app.config['USERNAME']:
#            error = 'Invalid username'
#        elif request.form['password'] != app.config['PASSWORD']:
#            error = 'Invalid password'
#        else:
#            session['logged_in'] = Tru
#            flash('You were logged in')
#            return redirect(url_For('show_entries'))
#    return render_template('login.html',error=error)

#@app.route('/logout')
#def logout():
#    session.pop('logged_in', None)
#    flash('You were logged out')
#    return redirect(url_For('show_entries'))
