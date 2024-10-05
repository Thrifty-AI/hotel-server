import requests
import uuid
import time
from flask import request
import os
import logging
import traceback
from dotenv import load_dotenv
load_dotenv()

AutoCancelDurationInMinutes = 3

(
    payment_merchant_id,
    payment_security_token,
    payment_api_url,
) = (
    os.environ.get("PAYMENT_MERCHANT_ID"),
    os.environ.get("PAYMENT_SECURITY_TOKEN"),
    os.environ.get("PAYMENT_API_URL"),
)
logging.info(f'PAYMENT_MERCHANT_ID: {os.environ.get("PAYMENT_MERCHANT_ID")}')
logging.info(f'PAYMENT_SECURITY_TOKEN: {os.environ.get("PAYMENT_SECURITY_TOKEN")}')
logging.info(f'PAYMENT_API_URL: {os.environ.get("PAYMENT_API_URL")}')

def init_payment(
    amount,
    payment_mode,
    userId,
    payment_imei,
    payment_pos_code,
    txn_id=None,
    forceSuccess=False,
    set_ptrn_callback=None,
):

    if txn_id is None:
        txn_id = uuid.uuid4().hex
    if amount < 1:
        return {
            "success": False or forceSuccess,
            "data": {
                "txn_id": txn_id,
                "message": f"Amount must be greater than 1rs. Amount : {amount}",
            },
        }

    if forceSuccess:
        return {
            "success": True,
            "data": {
                "txn_id": txn_id,
                "message": f"Amount must be greater than 1rs. Amount : {amount}",
            },
        }

    resp = None

    try:

        resp = requests.post(
            str(payment_api_url) + "/UploadBilledTransaction",
            json={
                "TransactionNumber": txn_id,
                "SequenceNumber": 1,
                "AllowedPaymentMode": payment_mode,
                "MerchantStorePosCode": payment_pos_code,
                "UserID": userId,
                "MerchantID": payment_merchant_id,
                "SecurityToken": payment_security_token,
                "IMEI": payment_imei,
                "AutoCancelDurationInMinutes": AutoCancelDurationInMinutes,
                "Amount": (
                    amount * 100
                    if os.environ.get("USE_ACTUAL_AMOUNT") == "true"
                    else 100
                ),
            },
        ).json()

    except Exception as e:
        logging.info(f'{traceback.format_exc()}')

        return {
            "success": False,
            "data": {
                "txn_id": txn_id,
                "message": "Something went wrong",
                "txn_data": [],
            },
        }

    ptrn = resp.get("PlutusTransactionReferenceID")
    logging.info(f"ptrn : {ptrn}")
    logging.info(f"txn_id : {txn_id}")
    logging.info(f"init payment resp data: {resp}")

    if callable(set_ptrn_callback):
        try:
            set_ptrn_callback(ptrn)
        except Exception:
            logging.info("error calling callback !!")
            logging.info(f"{traceback.format_exc()}")

    if resp.get("ResponseCode") != 0:
        return {
            "success": resp.get("ResponseCode") == 0 or forceSuccess,
            "data": {
                "ptrn": ptrn,
                "txn_id": txn_id,
                "message": resp.get("ResponseMessage"),
                "txn_data": (
                    resp["TransactionData"] if resp.get("TransactionData") else []
                ),
            },
        }

    status = None
    start_time = time.time()

    while status is None or status.get("ResponseCode") == 1001:
        if time.time() - start_time > AutoCancelDurationInMinutes * 60:
            status = {
                "ResponseCode": 1,
                "ResponseMessage": "TXN TIMEOUT",
                "TransactionData": (
                    status["TransactionData"] if status.get("TransactionData") else []
                ),
            }
            break
        try:
            status = get_payment_status(ptrn, payment_imei, payment_pos_code)
        except Exception:
            logging.info(f"{traceback.format_exc()}")
        time.sleep(3)

    return {
        "success": status.get("ResponseCode") == 0 or forceSuccess,
        "data": {
            "ptrn": ptrn,
            "txn_id": txn_id,
            "message": status.get("ResponseMessage"),
            "txn_data": status["TransactionData"],
        },
    }


def cancel_payment(
    amount,
    ptrn,
    payment_imei,
    payment_pos_code,
):

    if ptrn is None:
        return {
            "success": False,
            "data": {"ptrn": ptrn, "amount": amount},
            "message": "PTRN not provided",
        }

    try:

        resp = requests.post(
            payment_api_url + "/CancelTransaction",
            json={
                "MerchantID": payment_merchant_id,
                "SecurityToken": payment_security_token,
                "IMEI": payment_imei,
                "MerchantStorePosCode": payment_pos_code,
                "PlutusTransactionReferenceID": ptrn,
                "Amount": (
                    amount * 100
                    if os.environ.get("USE_ACTUAL_AMOUNT") == "true"
                    else 100
                ),
            },
        ).json()

        logging.info(f"cancel payment resp data : {resp}")

        return {
            "success": resp.get("ResponseCode") == 0,
            "data": {
                "ptrn": ptrn,
                "amount": amount,
                "message": resp.get("ResponseMessage"),
            },
        }

    except Exception as e:
        logging.info(
            f"Error while cancelling transaction for amount {amount} and ptrn : {ptrn}"
        )
        logging.info(f"{traceback.format_exc()}")
        return {
            "success": False,
            "data": {"ptrn": ptrn, "amount": amount},
            "message": "Something went wrong",
        }


def get_payment_status(ptrn, payment_imei, payment_pos_code):

    logging.info(f"getting payment status for ptrn : {ptrn}")

    resp = requests.post(
        payment_api_url + "/GetCloudBasedTxnStatus",
        json={
            "MerchantID": payment_merchant_id,
            "SecurityToken": payment_security_token,
            "IMEI": payment_imei,
            "MerchantStorePosCode": payment_pos_code,
            "PlutusTransactionReferenceID": ptrn,
        },
    ).json()

    return resp
