from flask import request, jsonify
from google.cloud import storage
from .final_text import process_document
from .final_text import process_compliment
from datetime import datetime
import os
import base64
import logging


data = [
    {
        "phone_number": "1234567890",
        "first_name": "Arnav",
        "last_name": "Palia",
        "verified": False,
        "payment": False,
    },
    {
        "phone_number": "1234567899",
        "first_name": "Satyam",
        "last_name": "Naman",
        "verified": True,
        "payment": False,
    },
]
room_data = [
    {
        "phone_number": "1234567899",
        "description": "Junior suit with king size bed",
        "images": ["../images/room2.png", "../images/room2.png"],
        "amount": 1,
        "room_type": "Deluxe Suit",
        "guests": "2 Adult(s) Mr Naman Singh Mrs Amita Singh",
        "from": "18 August 2024",
        "to": "20 August 2024",
        "gst": 50,
    },
    {
        "phone_number": "1234567890",
        "description": "Junior suit with king size bed",
        "images": ["../images/room1.png", "../images/room2.png"],
        "amount": 1,
        "room_type": "Deluxe Suit",
        "guests": "2 Adult(s) Mr Naman Singh Mrs Amita Singh",
        "from": "18 August 2024",
        "to": "20 August 2024",
        "gst": 50,
    },
]

images_urls = {
                'image_swimming_pool': ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/h1.jpeg','https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/h2.jpg'],
                'image_spa': ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/h3.jpeg', 'https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/h4.jpeg'],
                'image_fitness_center': ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/h5.jpeg', 'https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/h6.jpeg'],
                'image_business_center': ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/h7.jpg', 'https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/h8.jpeg'],
                'image_dining_hall': ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/h9.jpeg','https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/h10.jpeg'],
                'image_standard_room' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/h11.jpeg'],
                'image_deluxe_room' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/h12.jpg'],
                'image_balcony' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/P1.png'],
                'image_building' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/P2.png', 'https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/P3.png'],
                'image_rooftop' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/P4.png', 'https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/P5.png', 'https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/P6.png', 'https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/P7.png', 'https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/P8.png'],
                'image_dining_hall' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/P11.png'],
                'image_bedroom' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/P12.png', 'https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/P13.png'],
                'image_kitchen' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/P14.png'],
                'image_gym' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/p15.jpg', 'https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/p16.jpg'],
                'image_businessCentre' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/godrej1.png'],
                'image_club' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/godrej5.png'],
                'image_ground' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/godrej3.png'],
                'image_pool' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/godrej4.png'],
                'image_map' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/godrej2.png'],
               }


def register_routes(app):
    @app.route("/")
    def home():
        return "Hello, World!"

    @app.route("/fetch-details/<phone_number>", methods=["GET"])
    def fetch_details(phone_number):
        logging.info(f"request: {phone_number}")
        for i in data:
            if i["phone_number"] == str(phone_number):
                return jsonify({"users_details": i, "success": True}), 200

        return (
            jsonify(
                {"message": "Sorry, This number is not registered . Could you kindly share the phone number you used at the time of booking?", "success": False}
            ),
            200,
        )

    @app.route("/fetch-room-details/<booking_id>", methods=["GET"])
    def fetch_room_details(booking_id):
        # print("requesdsft: ", booking_id)
        for i in room_data:
            if i["phone_number"] == str(booking_id):
                return jsonify({"room_details": i, "success": True}), 200

        return jsonify({"message": "Invalid Booking ID", "success": False}), 200

    @app.route("/verify/<phone_number>", methods=["GET"])
    def verify(phone_number):

        for i in data:
            if i["phone_number"] == str(phone_number):
                i["verified"] = True
                return jsonify({"success": True}), 200

        # print(data)
        return jsonify({"success": False}), 404

    @app.route("/function-call", methods=["GET"])
    def handle_function_call():
        data = request.get_json()
        # print(data)
        if data["function_name"] == "checkin":
            return jsonify({"message": "Sure, Let's start with check in"}), 200

        if data["function_name"] == "checkout":
            return jsonify({"message": "Sure, Let's start with check out"}), 200

        return (
            jsonify({"message": "Sorry unable to process your request currently"}),
            200,
        )
    

    @app.route("/upload-document", methods=["POST"])
    def upload_image():
        logging.info("Request for document upload")
        try:
            # Get the data from the request
            data = request.json  # Assuming the image is sent as JSON
            image_data = data.get('image')

            if not image_data:
                return jsonify({"error": "No image data provided"}), 400
            
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            process_document(image_data)
            
            # Return a success message
            return jsonify({"message": "Image uploaded successfully"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    
    def fix_base64_padding(base64_string):
        """Fix base64 padding if necessary."""
        padding_needed = len(base64_string) % 4
        if padding_needed:
            base64_string += '=' * (4 - padding_needed)
        return base64_string

    @app.route("/capture-image", methods=["POST"])
    def capture_image():
        logging.info("Request for image compliment")
        try:
            # Get the data from the request
            data = request.json  # Assuming the image is sent as JSON
            image_data = data.get('image')

            if not image_data:
                return jsonify({"error": "No image data provided"}), 400
            
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]

            compliment = process_compliment(image_data)            
            # Return a success message
            return jsonify({"message": "Image uploaded successfully", "compliment": compliment}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        

    @app.route("/get-user-description", methods=["POST"])
    def get_user_description() :
        
        data = request.json
        response = {}
        logging.info("request to fetch user description")
        with open('user_description.txt', 'r') as file:
            response['compliment'] = file.read()
        try:
            logging.info(f"{response}")
            return jsonify({'message': response})
        
        except Exception as e: 
            return jsonify({"error": str(e)}), 500


    @app.route("/fetch-images", methods=['POST'])
    def fetch_images():
        logging.info(f"request to fetch image: {request}")
        response = {}
        data = request.get_json()
        if data['function_name'] in images_urls:
            response['urls'] = images_urls[data['function_name']]
            print(response)
            return {'message': response}
        
        return 'invalid function'

    @app.route('/wayfinder', methods=['POST'])
    def api_wayfinder():
        data = request.get_json()
        print(data)
        start = request.args.get('start')
        end = data.get('function_arguments')
        # print(type(end))
        url = wayfinder(start, end)
        print("url:", url)
        return jsonify({"message":{"urls": [url]}})

    def way_to_washroom():
        url_of_washroom = "https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/map_to_washroom.png"
        return url_of_washroom

    def way_to_foodCourt():
        url_of_foodCourt = "https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/map_to_foodcourt.png"
        return url_of_foodCourt

    def way_to_fireExit():
        url_of_fireExit = "https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/map_to_fireExit.png"
        return url_of_fireExit

    def wayfinder(start, end):
        end_str = end
        
        if isinstance(end, dict):
            end_str = end["destination"]
        if "washroom" in end_str.lower():
            return way_to_washroom()
        elif "food court" in end_str.lower():
            return way_to_foodCourt()
        elif "fire exit" in end_str.lower():
            return way_to_fireExit()
        else:
            return "Image url not present: " + end_str