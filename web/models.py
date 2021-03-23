from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from .utils import *

import datetime
from datetime import timedelta
from datetime import datetime as dt

today = datetime.date.today()
current_time = datetime.datetime.now()

### Custom User Model Used Here

class UserWallet(models.Model):
	user = models.OneToOneField('User', on_delete=models.CASCADE, default=None)
	walletID = models.CharField(max_length=100, default='')
	amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

	def __str__(self):
		return self.user.first_name + ' ' + self.user.last_name

class UserManager(BaseUserManager):
	"""
	Custom user model manager where email is the unique identifiers
	for authentication instead of username.
	"""
	def create_user(self, email, password, **extra_fields):
		"""
		Create and save a User with the given email and password.
		"""
		if not email:
			raise ValueError(_('The Email must be set'))
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save()
		return user

	def create_superuser(self, email, password, **extra_fields):
		"""
		Create and save a SuperUser with the given email and password.
		"""
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		extra_fields.setdefault('is_active', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError(_('Superuser must have is_staff=True.'))
		if extra_fields.get('is_superuser') is not True:
			raise ValueError(_('Superuser must have is_superuser=True.'))
		return self.create_user(email, password, **extra_fields)


#### This is User Profile
class User(AbstractUser):
	user_gender = (
		('Male', 'Male'),
		('Female', 'Female')
	)
	user_type = (
		('Beginner', 'Beginner'),
		('Resellers', 'Ressellers'),
		('Staff', 'Staff')
	)
	username = models.CharField(_('Username'), max_length=100, default='', unique=True)
	email = models.EmailField(_('email address'), unique=True)
	first_name = models.CharField(max_length=200, null=True)
	last_name = models.CharField(max_length=200, null=True)
	gender = models.CharField(max_length=10, default='', choices=user_gender)
	mobile = models.CharField(max_length=200, null=True)
	photo = models.ImageField(upload_to='users', default="/static/images/profile.png", null=True, blank=True)
	bio = models.TextField(default='', blank=True)
	account_type = models.CharField(max_length=10, default='Beginner', choices=user_type)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

	objects = UserManager()

	def __str__(self):
		return self.first_name + ' ' + self.last_name

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
	if created and instance.is_superuser == False:
		account_number = instance.mobile
		UserWallet.objects.create(user=instance, walletID=account_number)
		


#### This is user settings
class UserSettings(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
	account_verified = models.BooleanField(default=False)
	verified_code = models.CharField(max_length=100, default='', blank=True)
	verification_expires = models.DateField(default=dt.now().date() + timedelta(days=1))
	code_expired = models.BooleanField(default=False)
	recieve_email_notice = models.BooleanField(default=True)

	def __str__(self):
		return self.user.first_name + ' ' + self.user.last_name


#### User Payment History
class PayHistory(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
	paystack_charge_id = models.CharField(max_length=100, default='', blank=True)
	paystack_access_code = models.CharField(max_length=100, default='', blank=True)
	amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
	paid = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.username


class AlertVerify(models.Model):
	settings = models.OneToOneField(UserSettings, on_delete=models.CASCADE, default=None)
	sms_code = models.CharField(max_length=8, default='', blank=True)
	email_code = models.CharField(max_length=8, default='', blank=True)

	class Meta:
		verbose_name_plural = "Alert Verifications"

	def __str__(self):
		return self.settings.user.first_name + ' ' + self.settings.user.last_name


class UserPassToken(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
	token = models.CharField(max_length=100, default='', blank=True)
	expires_in = models.DateField(default=today + timedelta(days=1))
	expired = models.BooleanField(default=False)
	sent = models.BooleanField(default=False)

	def __str__(self):
		return self.user.email

@receiver(pre_save, sender=UserPassToken)
def update_expired(sender, instance, *args, **kwargs):
	if instance.expires_in < today:
		instance.expired = True
	else:
		instance.expired = False


class Contactinfo(models.Model):
    name = models.CharField(max_length = 50)
    email = models.EmailField()
    phone = models.CharField(max_length = 11)
    subject = models.CharField(max_length= 250)
    message = models.TextField()
	# date = models.DateTimeField(auto_now_add = True)	

    def __str__ (self):
        return self.name
