from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from image_recog import classify

import requests
import json
import ast
import picamera
import time
from datetime import date

#For getting a Quote
quote_params = {
	"dropoff_address" : "101 Market St, San Francisco, CA",
	"pickup_address" : "20 McAllister St, San Francisco, CA"
}

url = "https://api.postmates.com/"
quote_path = "/v1/customers/cus_KVDBsZcxJatwhk/delivery_quotes"
create_delivery_path = "/v1/customers/cus_KVDBsZcxJatwhk/deliveries"


api_quote_path = "{}{}".format(url, quote_path)
api_create_delivery_path = "{}{}".format(url, create_delivery_path)

API_KEY = "2c465122-3188-42b6-b5b6-d5e8d190e71b"
auth = (API_KEY, "")

inventory = [] 
order_details = [] 

def get_quote():
	r = requests.post(api_quote_path, data=quote_params, auth=auth)
	dict_r = ast.literal_eval(r.content)
	return dict_r

app = Flask(__name__)

@app.route("/api/add_item/", methods=['POST'])
def add_item():
	expiration_date = request.args['exp_date']
	name = request.args['name']

	inventory.append({"expiration_date" : expiration_date, "name" : name})
	print(expiration_date)
	return 'OK'

@app.route("/api/data/", methods=['GET'])
def get_data():
	return jsonify({"data" : data})

@app.route("/api/decide/", methods=['GET'])
def decide():	
	print(inventory)
	return 'OK'
@app.route("/api/get_order/", methods=['POST'])
def get_order():
	manifest = request.args['manifest']
	pickup_name = request.args['pickup_name']
	pickup_address = request.args['pickup_address']
	pickup_phone_number = request.args['pickup_phone_number']
	pickup_notes = request.args['pickup_notes']
	dropoff_name = request.args['dropoff_name']
	dropoff_address = request.args['dropoff_address']
	dropoff_notes = request.args['dropoff_notes']

	order_details.append({"manifest" : manifest, 
						  "pickup_name" : pickup_name,
						  "pickup_address" : pickup_address,
						  "pickup_phone_number" : pickup_phone_number,
						  "pickup_notes" : pickup_notes,
						  "dropoff_name" : dropoff_name,
						  "dropoff_address" : dropoff_address,
						  "dropoff_notes" : dropoff_notes})
	print(dropoff_notes)
	return "OK"

@app.route("/api/make_order/", methods=['POST'])
def make_order():
	data_in = {
		'id' : "{}".format(get_quote(['id'])),
		'manifest' : "{}".format(order_details["manifest"]),
		'pickup_name' : "{}".format(order_details["pickup_name"]),
		'pickup_address' : "{}".format(order_details["pickup_address"]),
		'pickup_phone_number' : "{}".format(order_details["pickup_phone_number"]),
		'pickup_notes' : "{}".format(order_details["pickup_notes"]),
		'dropoff_name' : "{}".format(order_details["dropoff_name"]),
		'dropoff_address' : "{}".format(order_details["dropoff_address"]),
		'dropoff_notes' : "{}".format(dropoff_notes)
	}
	r = requests.post(api_create_delivery_path, data=data_in, auth=auth)
	return r

@app.route("/scan")
def scan():
	with picamera.PiCamera() as camera:
		print("Please allow a moment for us to scan the object. Try to position the image to optimize focus.")
		time.sleep(5)
		camera.start_preview()
		time.sleep(15)
		camera.stop_preview()
		camera.capture('./imgs/in_01.jpg')
	classify('./imgs/in_01.jpg',inventory)
	return "Pleaaaaaaaaaaaase be my friend"

@app.route("/demo")
def demo():
	today = date(2015, 10, 11)
	week = date(2015, 10, 25)
	with open('inventory.txt') as f:
		for line in f:
			inventory.append(line)
	f.close()
	print(inventory)	
	while(today != week):
		for i in inventory:
			print(inventory[i])
		print(order_details)
		today = date(today.year, today.month, today.day+1)
	return "Ready to restock!"
@app.route("/")
def index():
	return(render_template('index.html'))
	#return 'OK'


if __name__ == "__main__":
    app.run(debug=True)
