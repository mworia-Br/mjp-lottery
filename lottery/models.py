from django.db import models
import datetime

class LotteryTicket(models.Model):
    player_phone_number = models.CharField(max_length=15)
    purchase_date = models.DateTimeField(auto_now_add=True)
    discarded = models.BooleanField(default=False)

    def __str__(self):
        return self.player_phone_number

class LotteryWinner(models.Model):
    phone_number = models.CharField(max_length=15)
    date_won = models.DateTimeField(default=datetime.datetime.now)
    amount_won = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.phone_number