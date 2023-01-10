import random

from django.shortcuts import render
from .models import LotteryTicket
from django.http import HttpResponse

from daraja_mpesa.mpesa import Mpesa

def initiate_stk_push(phone_number, amount):
    phone_number = phone_number
    amount = amount

    # The Mpesa class will automatically use the appropriate sandbox or production environment
    mpesa = Mpesa("<consumer_key>", "<consumer_secret>")
    stk_response = mpesa.stk_push(amount, phone_number, "Payment for Lottery Ticket")
    return stk_response


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