from flask import jsonify, request
import jwt
from datetime import datetime, timedelta
from bson import json_util
import json

from settings import app, bcrypt, secret, db
from models import User, TopUp, Transaction, TransactionType, Payment, Transfer
from tools import custom_auth

@app.route('/register', methods=['POST'])
def register():
    message = ""
    code = 500
    status = "Failed"
    try:
        data = request.get_json()     
        check_phone = User.objects(phone_number=data['phone_number']).count()
        
        if data['first_name'] is None:
            message = "Make sure first name must be filled"
            code = 400
        elif data['last_name'] is None:
            message = "Make sure last name must be filled"
            code = 400
        elif data['phone_number'] is None:
            message = "Make sure phone number must be filled"
            code = 400
        elif (7 <=  len(data['phone_number']) <= 13) is False:
            message = "Phone number must be filled between 7 to 13 digit"
            code = 400
        elif data['address'] is None:
            message = "Make sure address must be filled"
            code = 400
        elif data['pin'] is None:
            message = "Make sure PIN must be filled"
            code = 400
        elif check_phone >= 1:
            message = "User with this phone number already exists"
            code = 400
        else:
            data['pin'] = bcrypt.generate_password_hash(data['pin']).decode('utf-8')
            
            user = User(
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    phone_number=data['phone_number'],
                    address=data['address'],
                    pin=data['pin']
                ).save()
            
            status = "Successful"
            message = "User has registered successfully"
            code = 201
            
            return jsonify({'status': status, "message": message, 'result': user.serialize()}), code
    except Exception as ex:
        message = f"{ex}"
        status = "Failed"
        code = 500
    return jsonify({'status': status, "message": message}), code

@app.route('/login', methods=['POST'])
def login():
    message = ""
    code = 500
    status = "failed"
    try:
        data = request.get_json()
        
        if data['phone_number'] is None:
            message = "Make sure phone number must be filled"
            code = 400
            
        user = User.objects(phone_number=data['phone_number']).first()
        
        if data['pin'] is None:
            message = "Make sure PIN must be filled"
            code = 400
        elif user is None:
            message = "Phone number does not exists"
            code = 400
            status = "fail"
        elif user:
            user.user_id = str(user.user_id)
            if user and bcrypt.check_password_hash(user.pin, data['pin']):
                time = datetime.utcnow() + timedelta(hours=24)
                token = jwt.encode({
                        "user": {
                            "phone_number": f"{user.phone_number}",
                            "user_id": f"{user.user_id}",
                        },
                        "exp": time
                    },secret)

                # del user.pin
                res = {}
                code = 200
                status = "SUCCESS"
                res['access_token'] = token.decode('utf-8')
                
                return jsonify({'status': status, "result": res}), code

            else:
                message = "Wrong Pin"
                code = 400
                status = "Failed"
        else:
            message = "Invalid login details"
            code = 400
            status = "Failed"

    except Exception as ex:
        message = f"{ex}"
        code = 500
        status = "Failed"
    return jsonify({'status': status, "message":message}), code

@app.route('/top_up', methods=['POST'])
@custom_auth
def top_up(auth):
    user_id = auth['user']['user_id']
    code = 500
    status = "Failed"
    message = ""
    try:
        data = request.get_json()

        user = User.objects(user_id=user_id).first()

        if user is None:
            message = "User does not exists"
            code = 400
        elif data['amount'] is None:
            message = "Make sure amount must be filled"
            code = 400
        else:
            balance_before = user.balance
            balance_after = balance_before + data['amount']
            
            user.balance = balance_after
            user.save()
            
            top_up = TopUp(
                    amount=data['amount'],
                    balance_before=balance_before,
                    balance_after=balance_after,
                    user=user
                ).save()
            
            Transaction(
                transaction_type=TransactionType.CREDIT,
                top_up=top_up,
                user=user
            ).save()
            
            status = 'SUCCESS'
            code = 201
        
            return jsonify({'status': status, "result": top_up.serialize()}), code

    except Exception as ee:
        err = {"error": str(ee)}
    return jsonify({"status":status,'data': err, "message":message}), code

@app.route('/pay', methods=['POST'])
@custom_auth
def payment(auth):
    user_id = auth['user']['user_id']
    code = 500
    status = "Failed"
    message = ""
    try:
        data = request.get_json()

        user = User.objects(user_id=user_id).first()

        if user is None:
            message = "User does not exists"
            code = 400
        elif data['amount'] is None:
            message = "Make sure amount must be filled"
            code = 400
        elif data['remarks'] is None:
            message = "Make sure remarks must be filled"
            code = 400
        else:
            balance_before = int(user.balance)
            balance_after = balance_before - int(data['amount'])
            
            user.balance = balance_after
            user.save()
            
            payment = Payment(
                    amount=data['amount'],
                    remarks=data['remarks'],
                    balance_before=balance_before,
                    balance_after=balance_after,
                    user=user
                ).save()
            
            Transaction(
                transaction_type=TransactionType.DEBIT,
                payment=payment,
                user=user
            ).save()
            
            status = 'SUCCESS'
            code = 201
        
            return jsonify({'status': status, "result": payment.serialize()}), code

    except Exception as ee:
        err = {"error": str(ee)}
    return jsonify({"status":status,'data': err, "message":message}), code

@app.route('/transfer', methods=['POST'])
@custom_auth
def transfer(auth):
    user_id = auth['user']['user_id']
    code = 500
    status = "Failed"
    message = ""
    try:
        data = request.get_json()

        if data['target_user'] is None:
            message = "Make sure target user ID must be filled"
            code = 400

        user = User.objects(user_id=user_id).first()
        target_user = User.objects(user_id=data['target_user']).first()

        if user is None:
            message = "User does not exists"
            code = 400
        if target_user is None:
            message = "Target User does not exists"
            code = 400
        elif data['amount'] is None:
            message = "Make sure amount must be filled"
            code = 400
        elif data['remarks'] is None:
            message = "Make sure remarks must be filled"
            code = 400
        else:
            balance_before = int(user.balance)
            balance_after = balance_before - int(data['amount'])
            
            user.balance = balance_after
            user.save()
            
            target_user_balance_before = int(target_user.balance)
            target_user_balance_after = target_user.balance + int(data['amount'])
            
            target_user.balance = target_user_balance_after
            target_user.save()
            
            transfer = Transfer(
                    amount=data['amount'],
                    remarks=data['remarks'],
                    balance_before=balance_before,
                    balance_after=balance_after,
                    user=user,
                    target_user=target_user
                ).save()
            
            transfer_target = Transfer(
                    amount=data['amount'],
                    remarks=data['remarks'],
                    balance_before=target_user_balance_before,
                    balance_after=target_user_balance_after,
                    user=target_user,
                    from_user=user
                ).save()
            
            Transaction(
                transaction_type=TransactionType.DEBIT,
                transfer=transfer,
                user=user
            ).save()
            
            Transaction(
                transaction_type=TransactionType.CREDIT,
                transfer=transfer_target,
                user=target_user
            ).save()
            
            status = 'SUCCESS'
            code = 201
        
            return jsonify({'status': status, "result": transfer.serialize()}), code

    except Exception as ee:
        err = {"error": str(ee)}
    return jsonify({"status":status,'data': err, "message":message}), code

@app.route('/transactions', methods=['GET'])
@custom_auth
def transactions(auth):
    user_id = auth['user']['user_id']
    code = 500
    status = "Failed"
    message = ""
    try:

        user = User.objects(user_id=user_id)

        if user.first() is None:
            message = "User does not exists"
            code = 400
        else:
            
            transaction_list = []
            for item in Transaction.objects(user__in=user):
                if item.top_up is not None:
                    transaction_list.append(item.top_up.serialize())
                elif item.payment is not None:
                    transaction_list.append(item.payment.serialize())
                elif item.transfer is not None:
                    transaction_list.append(item.transfer.serialize())
            
            status = 'SUCCESS'
            code = 200
        
            return jsonify({'status': status, "result":transaction_list}), code

    except Exception as ee:
        err = {"error": str(ee)}
    return jsonify({"status":status,'data': err, "message":message}), code

@app.route('/profile', methods=['PUT'])
@custom_auth
def profile(auth):
    user_id = auth['user']['user_id']
    code = 500
    status = "Failed"
    message = ""
    try:
        data = request.get_json()

        user = User.objects(user_id=user_id).first()

        if user is None:
            message = "User does not exists"
            code = 400
        elif data['first_name'] is None:
            message = "Make sure first name must be filled"
            code = 400
        elif data['last_name'] is None:
            message = "Make sure last name remarks must be filled"
            code = 400
        elif data['address'] is None:
            message = "Make sure address must be filled"
            code = 400
        else:
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.address = data['address']
            user.save()
            
            status = 'SUCCESS'
            code = 201
        
            return jsonify({'status': status, "result": user.serialize()}), code

    except Exception as ee:
        err = {"error": str(ee)}
    return jsonify({"status":status,'data': err, "message":message}), code
