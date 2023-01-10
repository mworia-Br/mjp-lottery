import random

from django.shortcuts import render
from .models import LotteryTicket
from django.http import HttpResponse

def purchase_ticket(request):
    phone_number = request.GET.get('phone_number')
    ticket_price = 50

    # code to initiate mpesa transaction and handle the response
    # ...

    lottery_ticket = LotteryTicket.objects.create(
        player_phone_number=phone_number
    )
    return HttpResponse(f'Ticket purchased for {phone_number}')

def pick_winner():
    purchased_tickets = LotteryTicket.objects.all()
    if purchased_tickets.count() > 0:
        winner = random.choice(purchased_tickets)
        return winner.player_phone_number
    else:
        return None

def daily_draw(request):
    winner = pick_winner()
    total_collected = LotteryTicket.objects.count() * 50
    amount_to_be_won = total_collected * 0.3
    if winner:
        return HttpResponse(f'The winner of the daily draw is {winner}, winning ksh{amount_to_be_won}')
    else:
        return HttpResponse(f'No tickets were sold for today\'s draw')