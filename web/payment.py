import requests
import json
from django.http import HttpResponseRedirect
from fundme import settings
from .models import *

def init_payment(firstname, lastname, email, amount):
    url = 'https://api.paystack.co/transaction/initialize'
    headers = {
        'Authorization': 'Bearer '+settings.PAYSTACK_SECRET_KEY,
        'Content-Type' : 'application/json',
        'Accept': 'application/json',
        }
    datum = {
        "email": email,
        "amount": amount
        }
    x = requests.post(url, data=json.dumps(datum), headers=headers)
    if x.status_code != 200:
        print('not equl to 200')
        print (str(x.status_code))
    else:
        print('x.status is equal 200')
    results = x.json()
    # print('walaaaaaaaaaaaaaaaaaaas3')
    # print(x.status_code)
    # print(results)
    return results

# 
    # initialized = init_payment(firstname, lastname, email, amount)
    # print(initialized['data']['authorization_url'])
    # amount = amount/100
    # instance = PayHistory.objects.create(amount=amount, payment_for='wallet funding', user=request.user, paystack_charge_id=initialized['data']['reference'], paystack_access_code=initialized['data']['access_code'])
    # link = initialized['data']['authorization_url']
    # return HttpResponseRedirect(link)


    # initialized = init_payment(request)
    # print(initialized['data']['authorization_url'])
    # amount = amount/100
    # instance = PayHistory.objects.create(amount=amount, payment_for='wallet funding', user=request.user, paystack_charge_id=initialized['data']['reference'], paystack_access_code=initialized['data']['access_code'])
    # link = initialized['data']['authorization_url']
    # return HttpResponseRedirect(link)
    
    # 
    # initialized = init_payment(request)
	# print(initialized['data']['authorization_url'])
	# amount = amount/100
	# instance = PayHistory.objects.create(amount=amount, payment_for='wallet', user=request.user, paystack_charge_id=initialized['data']['reference'], paystack_access_code=initialized['data']['access_code'])
	# UserMembership.objects.filter(user=instance.user).update(reference_code=initialized['data']['reference'])
	# link = initialized['data']['authorization_url']
	# return HttpResponseRedirect(link)


    # print(initialized['data']['authorization_url'])
    # link = initialized['data']['authorization_url']
    # return HttpResponseRedirect(link)
