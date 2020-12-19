from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

import logging
import json
import uuid

# Create your models here.
class SplititUser(User):

    date_created = models.DateTimeField(null=True, blank=True)
    amount_owed = models.DecimalField(max_digits=7, decimal_places=1,default=0, blank=True)

    class Meta:
        verbose_name = "SplititUser"
        verbose_name_plural = "SplititUser"

    def save(self, *args, **kwargs):

        if self.pk == None:
            self.date_created = timezone.now()

        super(SplititUser, self).save(*args, **kwargs)