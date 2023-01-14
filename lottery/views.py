import random, africastalking, datetime, pytz
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from .models import LotteryTicket, LotteryWinner, MpesaTransaction
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

#from africastalking.AfricasTalkingGateway import AfricasTalkingGateway

from rest_framework.decorators import api_view
from rest_framework.response import Response


username = "sandbox"
api_key = "1e47b65816c33bfd5fc8ce975aed95d7e5d58b6a668e43310be632b7ee161610"
africastalking.initialize(username, api_key)

tz = pytz.timezone("Africa/Nairobi")
current_time = datetime.datetime.now(tz)
timestamp = current_time.strftime("%Y%m%d%H%M%S")

@csrf_exempt
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

def format_phone_number(phone_number):
    if phone_number.startswith("+254"):
        return "254" + phone_number[4:]
    elif phone_number.startswith("0"):
        return "254" + phone_number[1:]
    else:
        return None

@api_view(['GET'])
def mpesa_callback(request):
    # Get the transaction details from the request
    merchant_request_id = request.GET.get('MerchantRequestID')
    checkout_request_id = request.GET.get('CheckoutRequestID')
    result_code = request.GET.get('ResultCode')
    result_desc = request.GET.get('ResultDesc')
    amount = request.GET.get('Amount')
    mpesa_receipt_number = request.GET.get('MpesaReceiptNumber')
    transaction_date = request.GET.get('TransactionDate')
    phone_number = request.GET.get('PhoneNumber')
    if result_code == 0:
      # Create a new MpesaTransaction instance
        transaction = MpesaTransaction.objects.create(
            merchant_request_id=merchant_request_id,
            checkout_request_id=checkout_request_id,
            result_code=result_code,
            result_desc=result_desc,
            amount=amount,
            mpesa_receipt_number=mpesa_receipt_number,
            transaction_date=transaction_date,
            phone_number=phone_number
            )
        lottery_ticket = LotteryTicket.objects.create(
        player_phone_number=phone_number
        )
        data = {"status": "success", "transaction_id": transaction.merchant_request_id}
        return Response(data)
    else:
        data = {"status": "failed", "error": result_desc}
        return Response(data, status=400)



def initiate_stk_push(request, phone_number, amount):
    # Get the cart items and total cost
    phone_number = phone_number
    formatted_phone_number = format_phone_number(phone_number)
    amount = amount

    # Prepare the payload for the Mpesa STK push request
    payload = {
        "BusinessShortCode": "123456",
        "Password": "YOUR_PASSWORD",
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": formatted_phone_number,
        "PartyB": "123456",
        "PhoneNumber": formatted_phone_number,
        "CallBackURL": "https://braycodes.pythonanywhere.com/callback/",
        "AccountReference": "Ticket Purchase",
        "TransactionDesc": "Payment for ticket"
    }

    # Make the Mpesa STK push request
    stk_response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", 
        json=payload,
        headers={ "Authorization": "Bearer YOUR_ACCESS_TOKEN" }
    )

    # Check if the request was successful
    if stk_response.status_code == 200:
        # Save the transaction details in the database
        # Clear the cart
        # Redirect to the success page
        pass
    else:
        # Redirect to the error page
        pass
    return HttpResponse(f'Ticket purchased for {phone_number}. Response: {stk_response}')


"""
def initiate_stk_push(phone_number, amount):
    phone_number = phone_number
    amount = amount

    # The Mpesa class will automatically use the appropriate sandbox or production environment
    mpesa = Mpesa(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET)
    stk_response = mpesa.stk_push(amount, phone_number, "Payment for Lottery Ticket")
    return stk_response
"""
def purchase_ticket(request, phone_number):
    ticket_price = 50
    amount = ticket_price
    # initiate STK push
    initiate_stk_push(phone_number, amount)

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
    gateway = AfricasTalkingGateway("sandbox", "1e47b65816c33bfd5fc8ce975aed95d7e5d58b6a668e43310be632b7ee161610")
    
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
        return render(request, 'daily_draw.html')
    return render(request, 'daily_draw.html')

