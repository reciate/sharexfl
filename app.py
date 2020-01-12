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
	
@app.route('/gallery/<key>', methods=['GET'])
def gallery(key):
	name=getName(key)
	if name:
		return render_template('gallery.html', name=name, images=getImages(name))
	return abort(404)
	
@app.route('/u/<image>', methods=['GET'])
def u(image):
	return send_from_directory('u', image), 200
	
@app.route('/db/<table>', methods=['GET'])
def db(table):
	cursor = get_db().cursor()
	cursor.execute("SELECT * FROM {}".format(table))
	results = ' '.join(str(x) for x in cursor.fetchall())
	return results
	
with app.app_context():
	initdb()