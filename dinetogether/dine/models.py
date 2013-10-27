from django.db import models

# Create your models here.
from django.contrib.auth.models import (
	BaseUserManager, AbstractBaseUser
)

class MyUserManager(BaseUserManager):
	"""docstring for MyUserManager"""
	def create_user(self, email, password=None):
		if not email:
			raise ValueError('User must have an email address')

		user = self.model(
			email=MyUserManager.normalize_email(email)
		)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, password):
		user = self.create_user(email, password=password)
		user.is_admin = True
		user.save(using=self._db)
		return user

class MyUser(AbstractBaseUser):
	email = models.EmailField(
		verbose_name='email address',
		max_length=255,
		unique=True,
		db_index=True
	)
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)
	is_fb = models.BooleanField(default=False)
	fb_access_token = models.CharField(max_length=200)
	fb_user_id = models.IntegerField(default=False)

	objects = MyUserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	def get_full_name(self):
		return self.email

	def get_short_name(self):
		return self.email

	def __unicode__(self):
		return self.email

	def has_perm(self, perm, obj=None):
		return True

	def has_module_perms(self, app_label):
		return True

	def is_staff(self):
		"Is the user a member of staff?"
		return self.is_admin