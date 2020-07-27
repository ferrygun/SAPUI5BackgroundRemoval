import io
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import numpy as np
import time

from datetime import datetime
import requests
import logging
import argparse

from libs.strings import *
from libs.networks import model_detect
import libs.preprocessing as preprocessing
import libs.postprocessing as postprocessing

# Initialize the Flask application.
app = Flask(__name__)
CORS(app)

# Simple probe.
@app.route('/', methods=['GET'])
def hello():
    return 'Background Image Removal'

# Ping to wake up the BASNet service.
@app.route('/ping', methods=['GET'])
def ping():
    logging.info('ping')
    return 'pong'

# The paste endpoints handles new paste requests.
@app.route('/cut', methods=['POST'])
def save():
	start = time.time()
	logging.info(' CUT')
	
	# Convert string of image data to uint8.
	print(request.files)
	if 'data' not in request.files:
		return jsonify({
			'status': 'error',
			'error': 'missing file param `data`'
		}), 400
	data = request.files['data'].read()
	if len(data) == 0:
		return jsonify({'status:': 'error', 'error': 'empty image'}), 400

	with open('imgtmp.jpg', 'wb') as f:
		f.write(data)

	image = Image.open("imgtmp.jpg")
	print(image.size)

	input_path = 'imgtmp.jpg'
	output_path = 'imgtmp.png'
	model_name = 'u2net'
	preprocessing_method_name = 'none'
	postprocessing_method_name = 'fba'

	model = model_detect(model_name)  # Load model
	print("--model start--")
	
	preprocessing_method = preprocessing.method_detect(preprocessing_method_name)
	postprocessing_method = postprocessing.method_detect(postprocessing_method_name)
	wmode = "file"  # Get work mode
	image = model.process_image(input_path, preprocessing_method, postprocessing_method)
	
	image.save('imgtmp.png')

	# Save to buffer
	buff = io.BytesIO()
	image.save(buff, 'PNG')
	buff.seek(0)
	print("--model end--")

	# Print stats
	logging.info(f'Completed in {time.time() - start:.2f}s')
	print(f'Completed in {time.time() - start:.2f}s')

	return send_file(buff, mimetype='image/png')
	

if __name__ == '__main__':
    os.environ['FLASK_ENV'] = 'development'
    port = int(os.environ.get('PORT', 8082))
    app.run(debug=True, host='0.0.0.0', port=port)
