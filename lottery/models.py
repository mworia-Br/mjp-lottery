from django.db import models

class LotteryTicket(models.Model):
    player_phone_number = models.CharField(max_length=15)
    purchase_date = models.DateTimeField(auto_now_add=True)
    discarded = models.BooleanField(default=False)

    def __str__(self):
        return self.player_phone_number

class LotteryWinner(models.Model):
    phone_number = models.CharField(max_length=15)
    date_won = models.DateTimeField(auto_now_add=True)
    amount_won = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.phone_number

class MpesaTransaction(models.Model):
    merchant_request_id = models.CharField(max_length=255, unique=True)
    checkout_request_id = models.CharField(max_length=255, unique=True)
    result_code = models.IntegerField()
    result_desc = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_receipt_number = models.CharField(max_length=255, unique=True)
    transaction_date = models.DateTimeField()
    phone_number = models.CharField(max_length=255)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.mpesa_receipt_number

