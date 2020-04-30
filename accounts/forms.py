# from django.shortcuts import render, redirect
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from boto3.dynamodb.conditions import Key, Attr
import boto3
import botocore
import boto.dynamodb

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id='YOUR_KEY',
    aws_secret_access_key='YOUR_KEY',
    region_name='us-east-2')
table = dynamodb.Table('users')

def exists(self, attri):
		val = self.cleaned_data.get(attri)
		response = table.scan(FilterExpression = Attr(attri).eq(val))
		if len(response['Items']) == 0: # cannot find in db
			return False
		else:  # if already in db
			return True

class RegisterForm(forms.Form):
	username = forms.CharField(label='Username', min_length=4, max_length=150)
	email = forms.EmailField(label='Email')
	phone = forms.CharField(label='Phone')
	password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

	def clean_username(self):
		if exists(self, 'username'):
			raise ValidationError("Username already exist")
			
	def clean_email(self):
		if exists(self, 'email'):
			raise ValidationError("Email already exist")

	def clean_phone(self):
		if exists(self, 'phone'):
			raise ValidationError("Phone number already exist")
		phone = self.cleaned_data.get('phone')
		if len(phone) != 10:
			raise ValidationError("Wrong number")
		
	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')
		if password1 and password2 and password1 != password2:
		    raise ValidationError("Password don't match")
		elif len(password1) < 6:
			raise ValidationError("Length should longer than 6")
		return password2

class LoginForm(forms.Form):
	username = forms.CharField(label='Username', min_length=4, max_length=150)
	password = forms.CharField(label='Password', widget=forms.PasswordInput)
	def clean_password(self):
		if exists(self, 'username') is False:
			raise ValidationError("Wrong username")
		else:
			username = self.cleaned_data.get('username')
			password = self.cleaned_data.get('password')
			response = table.scan(FilterExpression = Attr('username').eq(username))
			ans = response['Items'][0]['password']
			if password != ans: # input password != password in DB
				raise ValidationError("Wrong password")

# class ResetPasswordForm(forms.Form):
class ResetPasswordForm(RegisterForm):

	def clean_username(self):
		if exists(self, 'username') is False:
			raise ValidationError("Username doesn't exist")
	def clean_email(self):
		if exists(self, 'email') is False:
			raise ValidationError("Email doesn't exist")
	def clean_phone(self):
		if exists(self, 'phone') is False:
			raise ValidationError("Phone number doesn't exist")

