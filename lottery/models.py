from django.db import models

class LotteryTicket(models.Model):
    player_phone_number = models.CharField(max_length=15)
    purchase_date = models.DateTimeField(auto_now_add=True)
    discarded = models.BooleanField(default=False)

    def __str__(self):
        return self.player_phone_number
