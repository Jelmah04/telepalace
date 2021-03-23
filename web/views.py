from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import *
from django.contrib.auth.hashers import make_password
from django.contrib import auth
from .serializers import RegisterSerializer
from .forms import SignUpForm
import datetime
from decimal import Decimal
from datetime import timedelta
from datetime import datetime as dt
import os
from django.conf import settings
from django.template.loader import render_to_string, get_template
from django.core.mail import message, send_mail, EmailMultiAlternatives
import requests
import json
import random
import string
import secrets
from django.http import HttpResponseRedirect
from twilio.rest import Client

from .payment import init_payment
import math
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt



# client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)

def gen_token(length=64, charset="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@$%-_"):
	return "".join([secrets.choice(charset) for _ in range(0, length)])

NUMERIC_CHARS = string.digits
STRING_LENGTH = 7

def generate_random_number(chars=NUMERIC_CHARS, length=STRING_LENGTH):
	return "".join(random.choice(chars) for _ in range(length))

today = datetime.date.today()


def home(request):
	return render(request, 'index.html')

def index(request):
	return render(request, 'dashboard.html')

def signin(request):
	if request.user.is_authenticated:
		return redirect('dashboard')
	return render(request, 'login.html')


def signin_ajax(request):
	if request.is_ajax():
		email = request.POST.get('email', None)
		password = request.POST.get('password', None)

		user = auth.authenticate(email=email, password=password)
		if user is not None:
			auth.login(request, user)
			response = {'success': 'Login Successfully. You will be redirect now.'}
			return JsonResponse(response)
		else:
			response = {'error': 'Error Email/Password. Try again.'}
			return JsonResponse(response)
	else:
		response = {'error': 'Check inputs and try again.'}
		return JsonResponse(response)


def check_mail_ajax(request):
	if request.is_ajax():
		email = request.GET.get('email', None)
		check_email = User.objects.filter(email=email).exists()
		if check_email == True:
			response = {'error': 'Email already exists.'}
			return JsonResponse(response)
		else:
			response = {'success': 'Cool'}
			return JsonResponse(response)
	else:
		response = {'error': 'Error Email Checking.'}
		return JsonResponse(response)
	

def check_username_ajax(request):
	if request.is_ajax():
		username = request.GET.get('username', None)
		check_username = User.objects.filter(username=username).exists()
		if check_username == True:
			response = {'error': 'Username already exists.'}
			return JsonResponse(response)
		else:
			response = {'success': 'This is cool.'}
			return JsonResponse(response)
	else:
		response = {'error': 'Error Username Checking.'}
		return JsonResponse(response)

def check_mobile_ajax(request):
	if request.is_ajax():
		mobile = request.GET.get('mobile', None)
		check_mobile = User.objects.filter(mobile=mobile).exists()
		if check_mobile == True:
			response = {'error': 'Mobile already exists.'}
			return JsonResponse(response)
		else:
			response = {'success': 'This is cool.'}
			return JsonResponse(response)
	else:
		response = {'error': 'Error Mobile Number Checking.'}
		return JsonResponse(response)


def register(request):
	return render(request, 'register.html')


def register_ajax(request):
	if request.is_ajax():
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			obj = form.save()
			otp_code = generateOTP()
			site_name = settings.SITE_NAME
			full_name = obj.first_name + ' ' + obj.last_name

			subject_file = os.path.join(settings.BASE_DIR, "mail/register/subject.txt")
			subject = render_to_string(subject_file, {'name': obj.first_name, 'site_name': site_name})
			from_email = settings.DEFAULT_EMAIL_SENDER
			to_email = [obj.email]

			register_message_file = os.path.join(settings.BASE_DIR, "mail/register/body.txt")
			register_message = render_to_string(register_message_file, {
														'first_name': obj.first_name, 'last_name': obj.last_name,
														'otp_code': otp_code, 'site_name': site_name,
													})

			message = EmailMultiAlternatives(subject=subject, body=register_message, from_email=from_email, to=to_email)

			html_template = os.path.join(settings.BASE_DIR, "mail/register/body.html")
			template = render_to_string(html_template, {
														'first_name': obj.first_name, 'last_name': obj.last_name,
														'otp_code': otp_code, 'site_name': site_name,
														})

			message.attach_alternative(template, "text/html")

			message.send()
			UserSettings.objects.create(
				user=obj,
				verified_code=otp_code
			)
			response = {'success': 'Registration successful. Kindly enter the OTP sent to your email address. ['+obj.email+']'}
			return JsonResponse(response)
		else:
			response = {'error': 'We could not process your request. Try again.'}
			return JsonResponse(response)
	else:
		response = {'error': 'Please check all fields and try again.'}
		return JsonResponse(response)


def verifyAccount(request):
	return render(request, 'verify_account.html')


def confirm_email_ajax(request):
	if request.is_ajax():
		otp_code = request.POST.get('otp_code', None)
		if otp_code:
			check_code = UserSettings.objects.filter(verified_code=otp_code).exists()
			if check_code:
				# get_user = UserSettings.objects.get(verified_code=otp_code)
				get_settings = UserSettings.objects.get(verified_code=otp_code)
				instance = UserSettings.objects.filter(id=get_settings.id).update(account_verified=True, code_expired=True)
				# User.objects.filter(user=instance.user)
				if instance:
					response = {
								 'success': 'Account Verified Successfully' # response message
								}
					return JsonResponse(response) # return response as JSON
				else:
					response = {
								 'error': 'Error verifying Account. Try again.' # response message
								}
					return JsonResponse(response) # return response as JSON
			else:
				response = {
					'error': 'Error Code. Check and try again.'
				}
				return JsonResponse(response)
		else:
			response = { 'error': 'Please input code and try again.' }
			return JsonResponse(response)


def reset_password_email(request):
	if request.is_ajax():
		email = request.POST.get('email', None)
		check_email = User.objects.filter(email=email).exists()
		if check_email == False:
			response = {'error': 'Email does not exists.'}
			return JsonResponse(response)
		# Email exists if the above error is not been throw
		# Let us send the email to the user
		user = User.objects.get(email=email)
		# Let's call the generate function to generate our token
		token = gen_token()
		first_name = user.first_name
		last_name = user.last_name
		site_name = settings.SITE_NAME
		password_link = settings.SITE_URL+'forgot-password/reset_password/?signature='+token

		# Let's setup variable's to add to our template
		subject_file = os.path.join(settings.BASE_DIR, "mail/reset_password/subject.txt")
		subject = render_to_string(subject_file, {'name': first_name, 'site_name': site_name})
		from_email = settings.DEFAULT_EMAIL_SENDER
		to_email = [email]

		password_message_file = os.path.join(settings.BASE_DIR, "mail/reset_password/body.txt")
		password_message = render_to_string(password_message_file, {
													'first_name': first_name, 'last_name': last_name,
													'password_link': password_link, 'site_name': site_name,
												})

		message = EmailMultiAlternatives(subject=subject, body=password_message, from_email=from_email, to=to_email)

		html_template = os.path.join(settings.BASE_DIR, "mail/reset_password/body.html")
		template = render_to_string(html_template, {
													'first_name': first_name, 'last_name': last_name,
													'password_link': password_link, 'site_name': site_name,
													})

		message.attach_alternative(template, "text/html")

		message.send()
		UserPassToken.objects.create(user=user, token=token, sent=True)
		response = {'success': 'Check your email for instructions'}
		return JsonResponse(response)


def reset_pass(request):
	if request.is_ajax():
		token = request.POST.get('signature', None)
		check_token = UserPassToken.objects.filter(token=token).exists()
		if check_token == False:
			response = {'error': 'Link has been expired. Try again.'}
			return JsonResponse(response)
		# Token exists.
		user_token = UserPassToken.objects.get(token=token)
		password1 = request.POST.get('new_password1')
		password2 = request.POST.get('new_password2')

		upper_case = sum(1 for c in password1 if c.isupper())
		digits = sum(1 for c in password1 if c.isdigit())
		chars = sum(1 for c in password1 if not c.isalnum())
		length = len(password1)

		if password2 != password1:
			return JsonResponse({'error': 'Password mismatch. Try again.'})
		elif length < 6:
			return JsonResponse({'error': 'Password is too short. Try another'})
		elif not upper_case:
			return JsonResponse({'error': 'Password must contain at least one Uppercase.'})
		elif not digits:
			return JsonResponse({'error': 'Password must contain at least one number.'})
		elif not chars:
			return JsonResponse({'error': 'Password must contain at least one character.'})

		new_password = make_password(password1)
		user = User.objects.get(id=user_token.user.id)
		user.password = new_password
		user.save()
		UserPassToken.objects.filter(token=token).update(expired=True)
		response = {'success': 'Password Reset Successful'}
		return JsonResponse(response)
	return render(request, 'password_reset_change.html')

def change_password (request):
	return render (request, 'change_password.html')



def dashboard (request):
	user_wallet = UserWallet.objects.get(user=request.user)
	pay_history = PayHistory.objects.filter(user=request.user)
	context = {
		'user_wallet': user_wallet.amount,
		'pay_history': pay_history
	}
	return render (request, 'dashboard.html', context)

def services (request):
	return render (request, 'services.html')

def wallet (request):
	return render (request, 'wallet.html')

def data (request):
	return render (request, 'data.html')

def cable (request):
	return render (request, 'cable.html')

def airtime (request):
	return render (request, 'airtime.html')

def electricity (request):
	return render (request, 'electricity.html')

def profile (request):
	return render (request, 'profile.html')

def funding (request):
	context = {
		'paystack_key': settings.PAYSTACK_PUBLIC_KEY
	}
	return render (request, 'funding.html', context)

class Verify_Payment(APIView):
	def get(self, request):
		user = request.user
		reference = request.GET.get("reference")
		url = 'https://api.paystack.co/transaction/verify/'+reference
		headers = {
			"Authorization": "Bearer " +settings.PAYSTACK_SECRET_KEY
		}
		x = requests.get(url, headers=headers)
		if x.json()['status'] == False:
			return False
		results = x.json()
		PayHistory.objects.create(user=user, paystack_charge_id=results["data"]["reference"], amount=results["data"]["amount"], paid=True)
		current_wallet = UserWallet.objects.get(user=user)
		current_wallet.amount += (results["data"]["amount"] /Decimal(100))
		current_wallet.save()

		return Response(results)

# @csrf_exempts
def contact (request):
	if request.method == 'POST':
		name = request.POST['name']
		email = request.POST['email']
		phone = request.POST['phone']
		subject = request.POST['subject']
		message= request.POST['message']

		contactinfo = Contactinfo(name=name,email=email,phone=phone,subject=subject,message=message)
		contactinfo.save()
		messages.success(request,'Your message has been sent successfully, we will get back to you soon!')
		return redirect('contact')
	else:
		print('am getting sooo bored')
	return render (request, 'contact.html')

def webhook (request):
	return render (request, 'webhook.html')

def transactionhistory (request):
	return render (request, 'transactionhistory.html')

def webhook (request):
	if request.method == 'POST':
		email = request.POST['email']
		amount = request.POST['payamount']
		firstname = request.user.first_name
		lastname = request.user.last_name
		amount = int(amount)*100

        # print(email)print(firstname)print(lastname)print(amount)
		initialized = init_payment(firstname, lastname, email, amount)
		print(initialized["data"]["authorization_url"])
		amount = amount/100
		instance = PayHistory.objects.create(amount=amount, user=request.user, paystack_charge_id=initialized['data']['reference'], paystack_access_code=initialized['data']['access_code'])

		wallet = UserWallet.objects.get(user=request.user)
		old_amt = wallet + amount
		wallet.save()
        
		link = initialized['data']['authorization_url']
		return HttpResponseRedirect(link)
	return render (request, 'webhook.html')

