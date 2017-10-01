import os
import sqlite3
import base64
import io
from PIL import Image
from flask import Flask,request,session,g,redirect,url_for,abort,render_template,flash,send_from_directory
from fpdf import FPDF
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.config.from_envvar('WAIVER_SETTINGS',silent=True)

def connect_db():
    """Connects to the specific database"""
    rv = sqlite3.connect(app.config['DATABASE'],detect_types=sqlite3.PARSE_DECLTYPES)
    rv.row_factory = sqlite3.Row
    return rv

def get_waiver():
    if not hasattr(g,'waiverText'):
        with app.open_resource('TrailsRoc  Group Run Waiver.docx.txt','r') as f:
            g.waiverText = f.read()
    return g.waiverText

def save_waiver_db(username,signdate,filename):
    db = get_db()

    shortName = filename.replace(app.config['UPLOAD_FOLDER'],'')

    cur = db.execute('select count(signdate) from waiverlist where signdate=? and username=?',(signdate,username))
    if cur.fetchone()[0] != 0:
        return

    cur = db.execute('insert into waiverlist (username,signdate,filename) values (?,?,?)',(username,signdate,shortName))
    db.commit()

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

def get_activities():
    db = get_db()
    cur = db.execute('select id,name from activities where activeP==1')
    entries = cur.fetchall()
    return entries

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.route('/')
def show_waiver():
    entries = get_activities()
    return render_template('show_waiver.html',waiver=get_waiver(),activities=entries)

@app.route('/sign',methods=['POST'])
def sign_waiver():
    return render_template('enter_signature.html',now=datetime.now())

def drawWaiver(pngName,username,date,outFN):
    pdf = FPDF('P','in','Letter')
    pdf.add_page()
    pdf.set_font('Arial','',32)
    pdf.cell(txt='#TrailsRoc Waiver',w=0,h=0.75,ln=1)
    pdf.set_font('Arial','',14)
    pdf.multi_cell(txt=get_waiver(),w=0,h=.20)
    pdf.image(pngName,w=8)
    pdf.cell(txt=username,w=0,h=.20,ln=1)
    pdf.cell(txt=date,w=0,h=.20,ln=1)
    pdf.output(outFN)

def getOutputPath(dt,ext,source='Flask'):
    d = dt.strftime('{}/{}/%Y/%m'.format(app.config['UPLOAD_FOLDER'],source))
    os.makedirs(d,exist_ok=True)
    if 'Flask' == source:
        return dt.strftime('{}/%Y%m%d-%H%M%S%f.{}'.format(d,ext))

def parseSQLTime(t):
    try:
        return datetime.strptime(t,'%Y-%m-%d %H:%M:%S.%f')
    except:
        return datetime.strptime(t,'%Y-%m-%d')

@app.route('/commit',methods=['POST'])
def commit_waiver():
    now = parseSQLTime(request.form['now'])
    pngName  = getOutputPath(now,'png')
    pdfName = getOutputPath(now,'pdf')
    png = Image.open(io.BytesIO(base64.b64decode(request.form['signature'].split(',')[1])))
    background = Image.new('RGBA', png.size, (255,255,255))
    alpha_composite = Image.alpha_composite(background, png)
    im2 = alpha_composite.convert(mode='P')
    im2.save(pngName,optimize=True)
    drawWaiver(pngName,request.form['username'],now.strftime('%Y-%m-%d'),pdfName)
    save_waiver_db(request.form['username'],now,pdfName)

    # I need the data at this point to create the PDF
    flash('New entry was successfully posted')
    return show_waiver()

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

def getYMD(t):
    year = t.strftime('%Y')
    month = t.strftime('%m')
    day = t.strftime('%d')
    return year,month,day

def get_fancy_waivers():
    db = get_db()
    cur = db.execute('select username,signdate,filename from waiverlist')

    entries = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(str))))
    for row in cur:
        t = parseSQLTime(row[1])
        year,month,day = getYMD(t)
        entries[year][month][day][row[0]] = 'uploads'+row[2]

    now = getYMD(datetime.now())
    return entries,now

@app.route('/list')
def list_waivers():
    entries,now = get_fancy_waivers()
    #entries = [x for x in sorted(os.listdir(app.config['UPLOAD_FOLDER'])) if 'pdf' in x]
    return render_template('list_waivers.html',entries=entries,now=now)

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
