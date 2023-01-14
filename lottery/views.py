import random

from django.shortcuts import render, redirect
from .models import LotteryTicket, LotteryWinner
from django.http import JsonResponse, HttpResponse

from daraja_mpesa.mpesa import Mpesa
from africastalking.AfricasTalkingGateway import AfricasTalkingGateway

def ussd_handler(request):
    session_id = request.GET.get("sessionId")
    service_code = request.GET.get("serviceCode")
    phone_number = request.GET.get("phoneNumber")
    text = request.GET.get("text")
    
    response = text.split("*")
    menu_level = len(response)

    if menu_level == 1:
        message = "Please select option:\n1. Purchase Ticket\n2. Check daily draw results"
        return JsonResponse({"response": message})

    elif menu_level == 2:
        if response[1] == "1":
            # calling the purchase_ticket view
            return redirect('purchase_ticket', phone_number=phone_number)
        elif response[1] == "2":
            message = 'Feature work in progress, check again soon'
            return JsonResponse({"response": message})
        else:
            message = "Invalid input. Please try again."
            return JsonResponse({"response": message})


def initiate_stk_push(phone_number, amount):
    phone_number = phone_number
    amount = amount

    # The Mpesa class will automatically use the appropriate sandbox or production environment
    mpesa = Mpesa(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET)
    stk_response = mpesa.stk_push(amount, phone_number, "Payment for Lottery Ticket")
    return stk_response

def purchase_ticket(request, phone_number):
    ticket_price = 50
    amount = ticket_price

    # initiate STK push
    stk_response = initiate_stk_push(phone_number, amount)

    if stk_response['response_code'] == '0':
        # Transaction was successful
        lottery_ticket = LotteryTicket.objects.create(
        player_phone_number=phone_number
        )
        return HttpResponse(f'Ticket purchased for {phone_number}. Response: {stk_response}')
    else:
        # Transaction failed
        return HttpResponse(f'Transaction failed with code: {stk_response["response_code"]}')

def discard_previous_tickets():
    LotteryTicket.objects.filter(discarded=False).update(discarded=True)

def pick_winner():
    purchased_tickets = LotteryTicket.objects.filter(discarded=False)
    if purchased_tickets.count() > 0:
        winner = random.choice(purchased_tickets)
        return winner.player_phone_number
    else:
        return None

def daily_draw(request):
    winner_phone_number = pick_winner()
    if winner_phone_number:
        total_collected = LotteryTicket.objects.filter(discarded=False).count() * 50
        amount_to_be_won = total_collected * 0.3
        discard_previous_tickets()
        # saving winner to db
        winner = LotteryWinner.objects.create(phone_number=winner_phone_number,amount_won=amount_to_be_won)
        send_winner_alert(winner_phone_number, amount_to_be_won)
        return HttpResponse(f'The winner of the daily draw is {winner_phone_number}, winning ksh{amount_to_be_won}')
    else:
        return HttpResponse(f'No tickets were sold for today\'s draw')

def send_winner_alert(phone_number, amount_won):
    # Initialize the SDK
    gateway = AfricasTalkingGateway("<username>", "<api_key>")
    
    # Define the message
    message = f'Congratulations! You have won Ksh{amount_won} in the daily lottery draw. Thank you for participating'
    
    # Send the message
    try:
        results = gateway.sendMessage(phone_number, message)
        for recipient in results:
            print(f'number={recipient["number"]},status={recipient["status"]},messageId={recipient["messageId"]}')
    except Exception as e:
        print(f'Encountered an error while sending: {e}')

def daily_draw_view(request):
    if request.method == 'POST':
        daily_draw(request)
        return redirect('lottery_ticket_changelist')
    return render(request, 'daily_draw.html')

