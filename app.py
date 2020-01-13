import random,string,sqlite3
from flask import Flask, request, send_from_directory,g,render_template,abort
app = Flask(__name__)

def genRandomString(length):
	return ''.join(random.choice(string.ascii_lowercase) for i in range(length))
	
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('db.db')
    return db
	
def initdb():
	db = get_db()
	cursor = db.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS keys(name text NOT NULL, key text NOT NULL, admin boolean NOT NULL, unique (name, key))")
	cursor.execute("CREATE TABLE IF NOT EXISTS uploads(name text NOT NULL, image text NOT NULL)")
	cursor.execute("INSERT OR IGNORE INTO keys (name, key, admin) VALUES (?,?,?)", ('Admin', 'CHANGEME', True))
	db.commit()
	
def keySearch(key):
	cursor = get_db().cursor()
	cursor.execute("SELECT * FROM keys WHERE key=?", (key,))
	if cursor.fetchone() is not None:
		return True
	return False
	
def getName(key):
	cursor = get_db().cursor()
	cursor.execute("SELECT * FROM keys WHERE key=?", (key,))
	result = cursor.fetchone()
	if result:
		return result[0]
	else:
		return None
		
def getImages(name):
	cursor = get_db().cursor()
	cursor.execute("SELECT * FROM uploads WHERE name=?", (name,))
	return cursor.fetchall()
	
def isAdmin(key):
	cursor = get_db().cursor()
	cursor.execute("SELECT * FROM keys where key=?", (key,))
	result = cursor.fetchone()
	if result:
		if result[2] == 1:
			return True
		return False
	return None

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/up', methods=['POST'])
def upload():
	try:
		if keySearch(request.form['key']) == False:
			return 'Your key is invalid!', 401
	except:
		return 'You must supply a key!', 401
	image = request.files['image']
	filename = '{}.png'.format(genRandomString(6))
	image.save('u/{}'.format(filename))
	db = get_db()
	cursor = db.cursor()
	cursor.execute("INSERT INTO uploads (name, image) VALUES (?,?)", (getName(request.form['key']), filename))
	db.commit()
	return '{}u/{}'.format(request.url_root, filename), 200
	
@app.route('/gallery', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		if keySearch(request.form['key']):
			name=getName(request.form['key'])
			return render_template('gallery.html', name=name, images=getImages(name))
	return render_template('login.html'), 200
	
@app.route('/admin', methods=['GET', 'POST'])
def admin():
	if request.method == 'POST' and isAdmin(request.form['key']):
		return render_template('admin.html', key=request.form['key']), 200
	return render_template('login.html'), 200
	
@app.route('/adduser', methods=['POST'])
def adduser():
	if isAdmin(request.form['adminKey']):
		if request.form['admin']:
			admin=True
		else:
			admin=False
		db = get_db()
		cursor = db.cursor()
		cursor.execute("INSERT OR IGNORE INTO keys (name, key, admin) VALUES (?,?,?)", (request.form['name'], request.form['key'], admin))
		db.commit()
		return '{} added successfully!'.format(request.form['name']), 200
	abort(404)
	
@app.route('/edituser', methods=['POST'])
def edituser():
	if isAdmin(request.form['adminKey']):
		db = get_db()
		cursor = db.cursor()
		cursor.execute("UPDATE keys SET key = ? WHERE name = ?", (request.form['key'], request.form['name']))
		db.commit()
		return '{} edited successfully!'.format(request.form['name']), 200
	abort(404)

@app.route('/u/<image>', methods=['GET'])
def u(image):
	return send_from_directory('u', image), 200
	
with app.app_context():
	initdb()