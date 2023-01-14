from django.contrib import admin

# Register your models here.
from .models import LotteryTicket, LotteryWinner

admin.site.register(LotteryTicket)
admin.site.register(LotteryWinner)