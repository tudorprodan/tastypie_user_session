from django.db import models
from django.contrib.auth.models import User

class UserFacebookAccount(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    facebook_id = models.BigIntegerField(db_index=True)
    user = models.OneToOneField(User, related_name="facebook_account")
