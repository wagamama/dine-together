# Create your views here.
from datetime import datetime
from django import forms
from django.utils import timezone
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout, get_user, get_user_model
from dine.models import Party, Restaurant, MyUser, UserParty, PartyComment, Schedule, RestaurantComment, RestaurantRef

class RegisterForm(forms.Form):
	email = forms.EmailField(max_length=30)
	password = forms.CharField(max_length=20)
	conf_password = forms.CharField(max_length=20)

class CreatePartyForm(forms.Form):
	name = forms.CharField(max_length=20)
	description = forms.CharField(max_length=200, widget=forms.Textarea)
	due_date = forms.DateTimeField(label='due date', input_formats=['%Y-%m-%d'], localize=True)

class AddRestaurantForm(forms.Form):
	name = forms.CharField(max_length=20)
	description = forms.CharField(max_length=200, widget=forms.Textarea)
	url = forms.URLField()
	address = forms.CharField(max_length=80)

def home(request):
	user = get_user(request)
	alive = []
	not_alive = []
	parties = Party.objects.filter(userparty__user=user.id).order_by('due_date')
	for p in parties:
		if p.is_alive():
			alive.append(p)
		else:
			not_alive.append(p)
	parties = alive + not_alive
	return render_to_response('dine/index.html', {'parties': parties}, context_instance=RequestContext(request))

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
				return HttpResponseRedirect('/')
				# Return a 'disabled account' error message
		else:
			return HttpResponseRedirect('/')
			# Return an 'invalid login' error message.
	return HttpResponseRedirect('/')

def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')

def vote_schedule(request, party_id):
	user = get_user(request)
	party = Party.objects.filter(id=party_id)
	if not party:
		return HttpResponseRedirect('/')
	party = party[0]
	up = UserParty.objects.filter(user=user.id, party=party_id)
	if not up:
		return HttpResponseRedirect('/')
	up = up[0]
	up.schedule_voted = True
	up.save()
	for schedule in party.schedule_set.all():
		vote = request.POST.get(str(schedule.id))
		if vote:
			schedule.votes += 1
			schedule.save()
	return HttpResponseRedirect('/dine/detail/p/%s/' % party_id)

def vote_restaurant(request, party_id):
	user = get_user(request)
	party = Party.objects.filter(id=party_id)
	if not party:
		return HttpResponseRedirect('/')
	party = party[0]
	up = UserParty.objects.filter(user=user.id, party=party_id)
	if not up:
		return HttpResponseRedirect('/')
	up = up[0]
	up.restaurant_voted = True
	up.save()
	for restaurant in party.restaurant_set.all():
		vote = request.POST.get("vote_restaurant")
		if vote == str(restaurant.id):
			restaurant.votes += 1
			restaurant.save()
	return HttpResponseRedirect('/dine/detail/p/%s/' % party_id)

def add_user(request, party_id):
	user = get_user(request)
	party = Party.objects.filter(id=party_id)
	if not party:
		return HttpResponseRedirect('/')
	party = party[0]
	email = request.POST.get("join_user")
	join_user = MyUser.objects.filter(email=email)
	if join_user:
		up = UserParty.objects.filter(user=join_user[0].id, party=party_id)
		if not up:
			up = UserParty(user=join_user[0], party=party)
			up.save()
	return HttpResponseRedirect('/dine/detail/p/%s/' % party_id)

def add_schedule(request, party_id):
	user = get_user(request)
	party = Party.objects.filter(id=party_id)
	if not party:
		return HttpResponseRedirect('/')
	party = party[0]
	date = datetime.strptime(request.POST.get("schedule_date"), "%Y-%m-%d")
	if date:
		schedule = Schedule.objects.filter(party=party_id, date=date)
		if not schedule:
			schedule = Schedule(party=party, date=date)
			schedule.save()
	return HttpResponseRedirect('/dine/detail/p/%s/' % party_id)

def add_restaurant_view(request, party_id):
	error_msg = False
	user = get_user(request)
	party = Party.objects.filter(id=party_id)
	if not party:
		return HttpResponseRedirect('/')
	party = party[0]
	if request.method == 'POST':
		form = AddRestaurantForm(request.POST)
		if form.is_valid():
			name = request.POST.get("name")
			address = request.POST.get("address")
			description = request.POST.get("description")
			url = request.POST.get("url")
			restaurant = party.restaurant_set.create(name=name, description=description, address=address, url=url)
			restaurant.save()
			return HttpResponseRedirect('/dine/detail/p/%s/' % party.id)
	return render_to_response('dine/add-restaurant.html', {'error_msg': error_msg}, context_instance=RequestContext(request))

def add_restaurant_ref(request, restaurant_id):
	user = get_user(request)
	restaurant = Restaurant.objects.filter(id=restaurant_id)
	if not restaurant:
		return HttpResponseRedirect('/')
	restaurant = restaurant[0]
	party = restaurant.party
	url = request.POST.get("url")
	if url:
		ref = RestaurantRef(restaurant=restaurant, url=url)
		ref.save()

	return HttpResponseRedirect('/dine/detail/r/%s/' % restaurant_id)

def create_party_view(request):
	error_msg = False
	user = get_user(request)
	if request.method == 'POST':
		form = CreatePartyForm(request.POST)
		if form.is_valid():
			name = request.POST.get("name")
			description = request.POST.get("description")
			due_date = datetime.strptime(request.POST.get("due_date"), "%Y-%m-%d")
			party = user.party_set.create(name=name, description=description, create_date=timezone.now(), due_date=due_date)
			party.save()
			up = UserParty(user=user, party=party)
			up.save()
			return HttpResponseRedirect('/dine/detail/p/%s/' % party.id)
		else:
			print "invalided"
			print form.errors
			error_msg = form.errors
	return render_to_response('dine/create-party.html', {'error_msg': error_msg}, context_instance=RequestContext(request))

def party_detail(request, party_id):
	user = get_user(request)
	winner = {'schedule': [], 'restaurant': []}
	owner = False
	party = Party.objects.filter(id=party_id)
	if not party:
		return HttpResponseRedirect('/')
	party = party[0]
	up = UserParty.objects.filter(user=user.id, party=party_id)
	if not up:
		return HttpResponseRedirect('/')
	up = up[0]
	users = MyUser.objects.filter(userparty__party=party_id)
	schedules = party.schedule_set.all().order_by('date')
	restaurants = party.restaurant_set.all()
	if not party.is_alive():
		if schedules.count():
			winner['schedule'] = sorted(list(schedules), key=lambda schedule: schedule.votes, reverse=True)[0]
		if restaurants.count():
			winner['restaurant'] = sorted(list(restaurants), key=lambda restaurant: restaurant.votes, reverse=True)[0]
	if party.user.id == user.id:
		owner = True
	elif not users.filter(id=user.id).exists():
		return HttpResponseRedirect('/')
	
	return render_to_response('dine/party.html', {'owner': owner, 'party': party, 'up': up, 'users': users, 'schedules': schedules, 'restaurants': restaurants, 'winner': winner}, context_instance=RequestContext(request))

def restaurant_detail(request, restaurant_id):
	user = get_user(request)
	owner = False
	restaurant = Restaurant.objects.filter(id=restaurant_id)
	if not restaurant:
		return HttpResponseRedirect('/')
	restaurant = restaurant[0]
	refs = restaurant.restaurantref_set.all()
	party = restaurant.party
	if party.user.id == user.id:
		owner = True

	return render_to_response('dine/restaurant.html', {'owner': owner, 'party': party, 'restaurant': restaurant, 'refs': refs}, context_instance=RequestContext(request))
