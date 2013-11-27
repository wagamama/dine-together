from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from dine.models import MyUser, Restaurant, Party, UserParty, PartyComment, UserRestaurant, RestaurantComment

class UserCreationForm(forms.ModelForm):
	"""docstring for UserCreationForm"""
	password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

	class Meta:
		model = MyUser
		fields = ('email', 'fb_access_token')

	def clean_password2(self):
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")
		return password2

	def save(self, commit=True):
		user = super(UserCreationForm, self).save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
		return user

class UserChangeForm(forms.ModelForm):
	password = ReadOnlyPasswordHashField()

	class Meta:
		model = MyUser

	def clean_password(self):
		return self.initial["password"]

class MyUserAdmin(UserAdmin):
	form = UserChangeForm
	add_form = UserCreationForm

	list_display = ('email', 'fb_access_token', 'fb_user_id', 'is_fb', 'is_admin')
	list_filter = ('is_admin',)
	fieldsets = (
		(None, {'fields': ('email', 'password')}),
		('Facebook info', {'fields': ('fb_access_token',)}),
		('Permissions', {'fields': ('is_admin',)}),
		('Important dates', {'fields': ('last_login',)}),
	)

	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'fb_access_token', 'password1', 'password2')}
		)
	)
	search_field = ('email',)
	ordering = ('email',)
	filter_horizontal = ()

class RestaurantInline(admin.StackedInline):
	model = Restaurant

class PartyAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields': ['user', 'name', 'description']}),
		('Date information', {'fields': ['create_date', 'due_date']})
	]
	inlines = [RestaurantInline]
	list_display = ('name', 'create_date', 'due_date', 'is_alive')

class UserPartyAdmin(admin.ModelAdmin):
	filedsets = [
		(None, {'fields': ['user', 'party', 'voted']}),
	]

class UserRestaurantAdmin(admin.ModelAdmin):
	filedsets = [
		(None, {'fields': ['user', 'restaurant', 'rated']}),
	]

admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Party, PartyAdmin)
admin.site.register(PartyComment)
admin.site.register(Restaurant)
admin.site.register(RestaurantComment)
admin.site.register(UserParty, UserPartyAdmin)
admin.site.register(UserRestaurant, UserRestaurantAdmin)
admin.site.unregister(Group)
