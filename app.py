import random,string
from flask import Flask, request, send_from_directory
app = Flask(__name__)

def genRandomString(length):
	return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

@app.route('/up', methods=['POST'])
def upload():
	image = request.files['image']
	filename = '{}.png'.format(genRandomString(6))
	image.save('u/{}'.format(filename))
	return '{}u/{}'.format(request.url_root, filename)
	
@app.route('/u/<image>', methods=['GET'])
def u(image):
	return send_from_directory('u', image)