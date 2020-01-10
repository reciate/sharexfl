import random,string,sqlite3
from flask import Flask, request, send_from_directory,g
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
	cursor.execute("CREATE TABLE IF NOT EXISTS uploads(key text NOT NULL, image text NOT NULL)")
	cursor.execute("INSERT OR IGNORE INTO keys (name, key, admin) VALUES (?,?,?)", ('Admin', 'Admin', True))
	db.commit()
	
def keySearch(key):
	cursor = get_db().cursor()
	cursor.execute("SELECT * FROM keys WHERE key=?", (key,))
	if cursor.fetchone() is not None:
		return True
	return False

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
	cursor.execute("INSERT INTO uploads (key, image) VALUES (?,?)", (request.form['key'], filename))
	db.commit()
	return '{}u/{}'.format(request.url_root, filename), 200
	
@app.route('/u/<image>', methods=['GET'])
def u(image):
	return send_from_directory('u', image), 200
	
@app.route('/db', methods=['GET'])
def db():
	cursor = get_db().cursor()
	cursor.execute("SELECT * FROM keys")
	data = cursor.fetchall()
	return ' '.join(str(x) for x in data)
	
with app.app_context():
	initdb()