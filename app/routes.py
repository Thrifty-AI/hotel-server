from flask import request, jsonify
from google.cloud import storage
from .final_text import process_document
from .final_text import process_compliment
from datetime import datetime
import os
import base64
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime


# Define OAuth scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

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
                'true' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/correct_answer.jpg'],
                'false' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/test_platform/wrong_answer.jpeg'],
                'image_4dx-features' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/4dx-features.png'],
                'image_handwash_steps': ['https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/handwash.png'],
                'image_maximization-chart-coffeeTree': ['https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/maximisation-chart-coffeeTree.png'],
                'image_maximization-chart-concessions': ['https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/maximisation-chart-concessions.png'],

                # Jubilant Images
                'image_2-cyanopyridine': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_2-cyanopyridine.png'],
                'image_4-cyanopyridine': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_4-cyanopyridine.png'],
                'image_alpha-picoline': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_alpha-picoline.png'],
                'image_beta-picoline': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_beta-picoline.png'],
                'image_3-cyanopyridine': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_3-cyanopyridine.png'],
                'image_piperidine': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_piperidine.png'],
                'image_gamma-picoline': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_gamma-picoline.png'],
                'image_pyridine': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_pyridine.png'],
                'image_pyridine-carbon-footprint': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_pyridine-carbon-footprint.png'],
                'image_3-cyano-pyridine-carbon-footprint': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_3-cyano-pyridine-carbon-footprint.png'],
                'image_ethical-procedures-chart': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_ethical-procedures-chart.png'],
                'image_project-management': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_project-management.png'],
                'image_pyridine_structure_pyridine-carbon-footprint': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_pyridine.png', 'https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_pyridine-carbon-footprint.png'],
                'image_pyridine-and-picolines': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_pyridine-and-picolines.png'],
                'image_picoline': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_picoline.png'],
                'image_cyanopyridine': ['https://storage.googleapis.com/public_thrifty_storage_bucket/jubilant/image_cyanopyridine.png'],
    

                #Ather Images
                'image_ather_rizta-s': ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_rizta-s.png'],
                'image_ather_rizta-z': ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_rizta-z.png'],
                'image_ather_pangong-blue-duo-colour' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_pangong-blue-duo-colour.png'],
                'image_ather_deccan-grey-mono-colour' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_deccan-grey-mono-colour.png'],
                'image_ather_siachen-white-mono-colour' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_siachen-white-mono-colour.png'],
                'image_ather_cardamom-green-duo-colour' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_cardamom-green-duo-colour.png'],
                'image_ather_deccan-grey-duo-colour' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_deccan-grey-duo-colour.png'],
                'image_ather_alphonso-yellow-duo-colour' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_alphonso-yellow-duo-colour.png'],
                'image_ather_pangong-blue-mono-colour' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_pangong-blue-mono-colour.png'],
                'image_ather_boot-space' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_boot-space.png'],
                'image_ather_dashboard' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_dashboard.png'],
                'image_ather_live-location' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_live-location.png'],
                'image_ather_ather-connect-app' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_ather-connect-app.png'],
                'image_ather_theft-tow-alerts' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_theft-tow-alerts.png'],
                'image_ather_rizta-front-view' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_rizta-front-view.png'],
                'image_ather_ping-my-scooter' : ['https://storage.googleapis.com/public_thrifty_storage_bucket/ather/image_ather_ping-my-scooter.png'],
                
                
  "image_trolley-sales-technique-serving": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_trolley-sales-technique-serving.png"
  ],
  "image_hybrid-concessions-upselling": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_hybrid-concessions-upselling.png"
  ],
  "image_coffeetree-transaction-process": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_coffeetree-transaction-process.png"
  ],
  "image_coffee-tree-order-serving": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_coffee-tree-order-serving.png"
  ],
  "image_4dx-effects": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_4dx-effects.png"
  ],
  "image_bill-me-back-office-print": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_bill-me-back-office-print.png"
  ],
  "image_maximization-chart-coffee-tree": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_maximization-chart-coffee-tree.png"
  ],
  "image_bill-me-back-office": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_bill-me-back-office.png"
  ],
  "image_bill-me-back-office-ebill": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_bill-me-back-office-ebill.png"
  ],
  "image_bill-me-back-office-bills": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_bill-me-back-office-bills.png"
  ],
  "image_hybrid-concessions-transaction": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_hybrid-concessions-transaction.png"
  ],
  "image_trolley-sales-technique-transaction": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_trolley-sales-technique-transaction.png"
  ],
  "image_4dx-locations": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_4dx-locations.png"
  ],
  "image_cinepolis-junior": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_cinepolis-junior.png"
  ],
  "image_maximization-chart-concessions": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_maximization-chart-concessions.png"
  ],
  "image_cinepolis_payment_process": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_cinepolis_payment_process.png"
  ],
  "image_handwash-process": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_handwash-process.png"
  ],
  "image_coffeetree-sales-technique": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_coffeetree-sales-technique.png"
  ],
  "image_cinepolis-concessions-serving": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_cinepolis-concessions-serving.png"
  ],
  "image_hybrid-concessions-order-serving": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_hybrid-concessions-order-serving.png"
  ],
  "image_order-of-service-preparation": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_order-of-service-preparation.png"
  ],
  "image_cinepolis-concessions-sales": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_cinepolis-concessions-sales.png"
  ],
  "image_trolley-sales-technique": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_trolley-sales-technique.png"
  ],
  "image_cinepolis-concessions-transaction": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_cinepolis-concessions-transaction.png"
  ],
  "image_cinepolis_sales_technique": [
    "https://storage.googleapis.com/public_thrifty_storage_bucket/cinepolis/image_cinepolis_sales_technique.png"
  ],

               }

redirect_link = {'contact-us': 'https://odysseymt.com/contact', 'about-us': 'https://odysseymt.com/about-us', 'placement': 'https://odysseymt.com/placement', 'blog': 'https://odysseymt.com/blog'}

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


    @app.route("/fetch-images2", methods=['POST'])
    def fetch_images2():
        logging.info(f"request to fetch image: {request}")
        response = {}
        data = request.get_json()
        if data['function']['enum_value'] in images_urls:
            response['urls'] = images_urls[data['function']['enum_value']]
            logging.info(response)
            return {'message': response}
        
        return 'invalid function'
    
    @app.route("/redirect_url", methods=['POST'])
    def redirect_url():
        logging.info(f"request to fetch redirect url: {request}")
        response = {}
        data = request.get_json()
        data = data['function']
        logging.info(f"type of received data: {type(data)}")
        if data['enum_value'] in redirect_link:
            response['urls'] = redirect_link[data['enum_value']]
            logging.info(f"response sent: {response}")
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

    @app.route('/google-calender', methods = ['GET'])
    def google_claender_api ():

        data = request.get_json()
        logging.info(f'request to google calender: {data}')
        params = data['function']['parameter']['meeting_details']

        params_list = [item.strip() for item in params.strip("[]").split(",")]

        if params_list and len(params_list) < 4:
            return jsonify({'error': 'missing arguments'}), 400
        
        if params_list[2].lower() == 'start time' or params_list[3].lower() == 'end time':
            return jsonify({'error': 'missing start or end time'}), 400

        try:
            service = authenticate_google()
            create_event(service)

            return jsonify({'message': 'Google calender api called successfully!'}), 200

        except Exception as e:

            return jsonify({'error': str(e)}), 500



    def create_event(service, summary, start_time, end_time, date): 
        timezone_addedTime= "05:30"
        timezone = 'Asia/Kolkata'
        """Create an event on the primary Google Calendar."""
        # Define event details
        event = {
            'summary': summary,
            # 'location': '123 Main Street, New York, NY',
            # 'description': 'Discuss project details and requirements.',
            'start': {
                'dateTime': f'{date}T{start_time}+{timezone_addedTime}',
                'timeZone': timezone,
            },
            'end': {
                'dateTime': f'{date}T{end_time}+{timezone_addedTime}',
                'timeZone': timezone,
            },

            # 'attendees': [
            #     {'email': 'example@gmail.com'}
            # ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 24 hours before
                    {'method': 'popup', 'minutes': 10},      # 10 minutes before
                ],
            },
        }

        # Add event to calendar
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        logging.info(f"Event created: {event_result.get('htmlLink')}")

    def authenticate_google():
        """Authenticate with Google OAuth2 and return an authorized Calendar service."""
        flow = InstalledAppFlow.from_client_secrets_file('../client_secrets.json')  # Path to client_secrets.json
        creds = flow.run_local_server(port=0)
        service = build('calendar', 'v3', credentials=creds)
        return service
