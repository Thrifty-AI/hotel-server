from flask_socketio import SocketIO, emit, disconnect
from flask import request
from .payments import init_payment, cancel_payment
import logging
import traceback
import uuid

state = {}

socketio = SocketIO()


def handle_connect():
    try:
        print(request.args)
        args = request.args
        state[request.sid] = {}

        # Validate all required keys are present
        required_keys = ["bookingId", "posId", "imei"]
        missing_keys = [key for key in required_keys if key not in args]

        if missing_keys:
            error_message = f"Missing keys: {', '.join(missing_keys)}"
            print(error_message)
            emit("error", error_message)
            disconnect()
            # return disconnect()

        # # Store validated keys
        # for key in required_keys:
        #     state[request.sid][key] = args[key]

        # try:
        #     init_payment(
        #         100,
        #         args['paymentMode'],
        #         request.sid,
        #         args['posImei'],
        #         args['posId']
        #     )
        # except Exception as e:
        #     logging.error(f"Payment initialization failed: {e}")
        #     emit('error', 'Payment initialization failed')
        #     # Ensure the message is sent before disconnecting
        #     socketio.sleep(0)
        #     disconnect()
        #     return

        amount = 100
        
        
        state[request.sid] = {
            "amount": amount,
            "posId": args["posId"],
            "imei": args["imei"]
        }      
        
        print("connected !")
        emit("message", {"data": "Connected to server"})

    except Exception as e:
        emit("error", "An unexpected error occurred")
        socketio.sleep(0)
        disconnect()

def handle_payment(payment_mode):
    
    imei = state[request.sid]['imei']
    pos = state[request.sid]["posId"]
    amount = state[request.sid]["amount"]

    def set_ptrn(ptrn):
        state[request.sid]["ptrn"] = ptrn
        
    userId = uuid.uuid4().hex

    txn_resp = init_payment(
        amount, payment_mode, userId, imei, pos, set_ptrn_callback=set_ptrn, forceSuccess=False
    )

    logging.info(f"txn_resp : {txn_resp}")

    if not txn_resp.get("success"):
        error_msg = txn_resp.get("data", {}).get("message", "Something went wrong")
        logging.info(f"payment error : {error_msg}")
        state[request.sid].pop("ptrn", None)
        return emit("payment_failed", error_msg)

    state[request.sid].pop("ptrn", None)
    emit("payment_success", "Payment successful")


def handle_disconnect():
    # You can perform cleanup or logging here
    print("Client disconnected")
    if state.get(request.sid, {}).get("ptrn"):
        logging.info(f"cancelling transaction {state[request.sid]['ptrn']}")
        cancel_payment(
            state[request.sid]["amount"],
            state[request.sid]["ptrn"],
            state[request.sid]["imei"],
            state[request.sid]["pos"],
        )
    state.pop(request.sid, None)
    
def handle_cancel_payment():
    if not state.get(request.sid, {}).get("ptrn"):
        return emit("error", "no ongoing transaction")
    logging.info(f"cancelling transaction {state[request.sid]['ptrn']}")
    cancel_payment(
        state[request.sid]["amount"],
        state[request.sid]["ptrn"],
        state[request.sid]["imei"],
        state[request.sid]["pos"],
    )
    state[request.sid].pop("ptrn",None)


socketio.on_event("connect", handle_connect)
socketio.on_event("disconnect", handle_disconnect)
socketio.on_event("payment", handle_payment)
socketio.on_event("cancel_payment", handle_cancel_payment)


@socketio.on_error_default
def default_error_handler(e):
    logging.info(traceback.format_exc())
    print(traceback.format_exc())
    emit("error", f"error occured : {request.event['message']}")
