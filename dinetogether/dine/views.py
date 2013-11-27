# Create your views here.
from django import forms
from django.utils import timezone
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout, get_user, get_user_model
from dine.models import Party, Restaurant, MyUser, UserParty, PartyComment, UserRestaurant, RestaurantComment

class RegisterForm(forms.Form):
	email = forms.EmailField(max_length=30)
	password = forms.CharField(max_length=20)
	conf_password = forms.CharField(max_length=20)

class CreatePartyForm(forms.Form):
	name = forms.CharField(max_length=20)
	description = forms.CharField(max_length=200, widget=forms.Textarea)
	due_date = forms.DateTimeField(label='due date', input_formats=['%Y-%m-%d'])

def home(request):
	alive = []
	not_alive = []
	host_parties = []
	guest_parties = []
	user = get_user(request)
	for p in Party.objects.filter(user=user.id).order_by('due_date'):
		if p.is_alive():
			alive.append(p)
		else:
			not_alive.append(p)
	host_parties = alive + not_alive
	alive = []
	not_alive = []
	ups = UserParty.objects.filter(user=user.id)
	parties = []
	if ups:
		for up in ups:
			parties.append(Party.objects.get(id=up.party.id))
	sorted(parties, key=lambda party: party.due_date)
	for p in parties:
		if p.is_alive():
			alive.append(p)
		else:
			not_alive.append(p)
	guest_parties = alive + not_alive
	return render_to_response('dine/index.html', {'host_parties': host_parties, 'guest_parties': guest_parties}, context_instance=RequestContext(request))

def register(request):
	error_msg = False
	User = get_user_model()
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			email = request.POST.get("email")
			password = request.POST.get("password")
			conf_password = request.POST.get("conf_password")
			if not password == conf_password:
				error_msg = "password not equal"
			else:
				u = User.objects.filter(email=email)
				if not u:
					user = User.objects.create_user(email, password)
					user.save()
					user = authenticate(username=email, password=password)
					login(request, user)
					return HttpResponseRedirect('/')
				else:
					print "user is exist"
					error_msg = "user is exist"
		else:
			print "invalided"
			error_msg = form.errors
	return render_to_response('dine/register.html', {'error_msg': error_msg}, context_instance=RequestContext(request))

def login_view(request):
	if request.method == 'POST':
		email = request.POST.get("email")
		password = request.POST.get("password")
		user = authenticate(username=email, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				# Redirect to a success page.
				print "login success"
				return HttpResponseRedirect('/')
			else:
				return HttpResponse('1')
				# Return a 'disabled account' error message
		else:
			return HttpResponseRedirect('/')
			# Return an 'invalid login' error message.
	return HttpResponseRedirect('/')

def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')

def create_party_view(request):
	error_msg = False
	user = get_user(request)
	if request.method == 'POST':
		form = CreatePartyForm(request.POST)
		if form.is_valid():
			name = request.POST.get("name")
			description = request.POST.get("description")
			due_date = request.POST.get("due_date")
			p = user.party_set.create(name=name, description=description, create_date=timezone.now(), due_date=due_date)
			p.save()
			return HttpResponseRedirect('/dine/detail/p/%s/' % p.id)
		else:
			print "invalided"
			print form.errors
			error_msg = form.errors
	return render_to_response('dine/create-party.html', {'error_msg': error_msg}, context_instance=RequestContext(request))

def create_restaurant_view(request):
	return HttpResponse("create_restaurant_view")

def party_detail(request, party_id):
	user = get_user(request)
	party = Party.objects.get(pk=party_id)
	restaurants = party.restaurant_set.all()
	if party.user.id == user.id:
		return render_to_response('dine/party.html', {'role': 'host', 'party': party, 'restaurants':restaurants}, context_instance=RequestContext(request))
	else:
		ups = UserParty.objects.filter(user=user.id)
		if ups and int(party_id)== ups[0].party.id:
			return render_to_response('dine/party.html', {'role': 'guest', 'party': party, 'restaurants':restaurants}, context_instance=RequestContext(request))
		else:
			return render_to_response('dine/party.html', {}, context_instance=RequestContext(request))

def restaurant_detail(request, restaurant_id):
	restaurant = Restaurant.objects.get(pk=restaurant_id)
	return HttpResponse("Let's dine at " % restaurant.name)
