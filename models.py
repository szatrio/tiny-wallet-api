import datetime
import uuid

from settings import db
from enum import Enum


class User(db.Document):
    user_id = db.UUIDField(binary=False, default=uuid.uuid4())
    first_name = db.StringField(required=True)
    last_name = db.StringField(required=True)
    phone_number = db.StringField(required=True, unique=True, min_length=7, max_length=13)
    address = db.StringField(required=True)
    pin = db.StringField(required=True)
    balance = db.IntField(required=True, default=0)
    created_date = db.DateTimeField(default=datetime.datetime.now, required=True)
    
    def __repr__(self):
        return '<User %s %s>' % (self.first_name, self.last_name)

    def serialize(self):
        return {
            'user_id'         : self.user_id,
            'first_name'      : self.first_name,
            'last_name'       : self.last_name,
            'phone_number'    : self.phone_number,
            'address'         : self.address,
            'created_date'    : self.created_date,
        }
        
class TopUp(db.Document):
    top_up_id = db.UUIDField(binary=False, default=uuid.uuid4())
    amount = db.IntField(required=True)
    balance_before = db.IntField(required=False)
    balance_after = db.IntField(required=True)
    created_date = db.DateTimeField(default=datetime.datetime.now, required=True)
    user = db.ReferenceField(User)

    meta = {'allow_inheritance': True}
    
    def __repr__(self):
        return '<Top Up %s %s>' % (self.user.user_id, self.amount)

    def serialize(self):
        return {
            'top_up_id'         : self.top_up_id,
            'user_id'           : self.user.user_id,
            'amount'            : self.amount,
            'balance_before'    : self.balance_before,
            'balance_after'     : self.balance_after,
            'created_date'      : self.created_date
        }
        
class Payment(db.Document):
    payment_id = db.UUIDField(binary=False, default=uuid.uuid4())
    amount = db.IntField(required=True)
    remarks = db.StringField(required=False)
    balance_before = db.IntField(required=False)
    balance_after = db.IntField(required=True)
    created_date = db.DateTimeField(default=datetime.datetime.now, required=True)
    user = db.ReferenceField(User)

    meta = {'allow_inheritance': True}
    
    def __repr__(self):
        return '<Payment %s %s>' % (self.user.user_id, self.amount)

    def serialize(self):
        return {
            'payment_id'        : self.payment_id,
            'user_id'           : self.user.user_id,
            'amount'            : self.amount,
            'remarks'           : self.remarks,
            'balance_before'    : self.balance_before,
            'balance_after'     : self.balance_after,
            'created_date'      : self.created_date
        }
        
class Transfer(db.Document):
    transfer_id = db.UUIDField(binary=False, default=uuid.uuid4())
    amount = db.IntField(required=True)
    remarks = db.StringField(required=False)
    balance_before = db.IntField(required=False)
    balance_after = db.IntField(required=True)
    created_date = db.DateTimeField(default=datetime.datetime.now, required=True)
    user = db.ReferenceField(User)
    target_user = db.ReferenceField(User, required=False)
    from_user = db.ReferenceField(User, required=False)

    meta = {'allow_inheritance': True}
    
    def __repr__(self):
        return '<Transfer %s %s>' % (self.user.user_id, self.amount)

    def serialize(self):
        return {
            'transfer_id'       : self.transfer_id,
            'user_id'           : self.user.user_id,
            'target_user_id'    : self.target_user.user_id if self.target_user else '',
            'from_user_id'      : self.from_user.user_id if self.from_user else '',
            'amount'            : self.amount,
            'remarks'           : self.remarks,
            'balance_before'    : self.balance_before,
            'balance_after'     : self.balance_after,
            'created_date'      : self.created_date
        }
        
class TransactionType(Enum):
    DEBIT = 'debit'
    CREDIT = 'credit'

class Transaction(db.Document):
    transaction_id = db.UUIDField(binary=False, default=uuid.uuid4())
    transaction_type = db.EnumField(TransactionType, required=True)
    user = db.ReferenceField(User, required=True)
    top_up = db.ReferenceField(TopUp, required=False)
    payment = db.ReferenceField(Payment, required=False)
    transfer = db.ReferenceField(Transfer, required=False)

    meta = {'allow_inheritance': True}
    
    def __repr__(self):
        return '<Transaction %s %s>' % (self.user.user_id, self.transaction_id)