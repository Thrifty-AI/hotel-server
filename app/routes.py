from flask import request, jsonify

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
        "images": ["../images/room1.png", "../images/room2.png"],
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


def register_routes(app):
    @app.route("/")
    def home():
        return "Hello, World!"

    @app.route("/fetch-details/<phone_number>", methods=["GET"])
    def fetch_details(phone_number):
        # print("request: ", phone_number)
        for i in data:
            if i["phone_number"] == str(phone_number):
                return jsonify({"users_details": i, "success": True}), 200

        return (
            jsonify(
                {"message": "No user with this phone number found", "success": False}
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
