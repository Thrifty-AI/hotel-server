import requests
import uuid
import time
from flask import request
import os
import logging
import traceback

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
            payment_api_url + "/UploadBilledTransaction",
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
        print(traceback.format_exc())

        return {
            "success": False,
            "data": {
                "txn_id": txn_id,
                "message": "Something went wrong",
                "txn_data": [],
            },
        }

    ptrn = resp.get("PlutusTransactionReferenceID")
    print(f"ptrn : {ptrn}")
    print(f"txn_id : {txn_id}")
    print(f"init payment resp data: {resp}")

    if callable(set_ptrn_callback):
        try:
            set_ptrn_callback(ptrn)
        except Exception:
            print("error calling callback !!")
            print(traceback.format_exc())

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
            print(traceback.format_exc())
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

        print(f"cancel payment resp data : {resp}")

        return {
            "success": resp.get("ResponseCode") == 0,
            "data": {
                "ptrn": ptrn,
                "amount": amount,
                "message": resp.get("ResponseMessage"),
            },
        }

    except Exception as e:
        print(
            f"Error while cancelling transaction for amount {amount} and ptrn : {ptrn}"
        )
        print(traceback.format_exc())
        return {
            "success": False,
            "data": {"ptrn": ptrn, "amount": amount},
            "message": "Something went wrong",
        }


def get_payment_status(ptrn, payment_imei, payment_pos_code):

    print(f"getting payment status for ptrn : {ptrn}")

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
