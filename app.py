import random,string
from flask import Flask, request
app = Flask(__name__)

def genRandomString(length):
	return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

@app.route('/up', methods=['POST'])
def upload():
	image = request.files['image']
	filename = '{}.png'.format(genRandomString(6))
	image.save('u/{}'.format(filename))
	return '{}u/{}'.format(request.url_root, filename)