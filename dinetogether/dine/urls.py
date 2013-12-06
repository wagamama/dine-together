from django.conf import settings
from django.conf.urls import patterns, url
from django.conf.urls.static import static

from dine import views

urlpatterns = patterns('',
	url(r'^$', views.home),
	url(r'^home', views.home),
	url(r'^register$', views.register),
	url(r'^login', views.login_view),
	url(r'^logout', views.logout_view),
	url(r'^create_party', views.create_party_view),
	url(r'^detail/p/(?P<party_id>\d+)/$', views.party_detail),
	url(r'^detail/p/(?P<party_id>\d+)/add_user', views.add_user),
	url(r'^detail/p/(?P<party_id>\d+)/add_schedule', views.add_schedule),
	url(r'^detail/p/(?P<party_id>\d+)/add_restaurant', views.add_restaurant_view),
	url(r'^detail/r/(?P<restaurant_id>\d+)/$', views.restaurant_detail),
	url(r'^detail/r/(?P<restaurant_id>\d+)/add_ref', views.add_restaurant_ref),
	url(r'^detail/p/(?P<party_id>\d+)/vote_schedule', views.vote_schedule),
	url(r'^detail/p/(?P<party_id>\d+)/vote_restaurant', views.vote_restaurant),
)

