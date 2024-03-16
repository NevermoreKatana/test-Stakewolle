from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
from dateutil import parser

USER_MODEL = get_user_model()


class ReferralCode(models.Model):
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True)
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_referral_code()
        super().save(*args, **kwargs)

    def generate_referral_code(self):
        import string
        import random
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
        return code

    def is_expired(self):
        date_object = parser.parse(self.expiry_date)
        return datetime.now() > date_object

class Referral(models.Model):
    referrer = models.ForeignKey(USER_MODEL, related_name='referrals', on_delete=models.CASCADE)
    referral = models.ForeignKey(USER_MODEL, related_name='referred_by', on_delete=models.CASCADE)