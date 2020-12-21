from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

import logging
import json
import uuid


class SplititUser(User):

    date_created = models.DateTimeField(null=True, blank=True)
    amount_owed = models.DecimalField(
        max_digits=7, decimal_places=1, default=0, blank=True)

    amount_paid = models.DecimalField(
        max_digits=7, decimal_places=1, default=0, blank=True)

    class Meta:
        verbose_name = "SplititUser"
        verbose_name_plural = "SplititUser"

    def save(self, *args, **kwargs):

        if self.pk == None:
            self.date_created = timezone.now()

        super(SplititUser, self).save(*args, **kwargs)


class SplititGroup(models.Model):

    id = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=300, blank=True, null=True)
    created_by = models.ForeignKey(
        SplititUser, related_name="created_by", null=True, blank=True, on_delete=models.SET_NULL)
    members = models.ManyToManyField(SplititUser, blank=True)
    to_simplify = models.BooleanField(blank=True, default=False)
    created_date = models.DateTimeField(null=True, blank=True)
    modified_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "SplititGroup"
        verbose_name_plural = "SplititGroups"

    def save(self, *args, **kwargs):

        if self.id == None or self.id == "":
            self.created_date = timezone.now()
            self.modified_date = timezone.now()
            self.id = str(uuid.uuid4())
        else:
            self.modified_date = timezone.now()

        super(SplititGroup, self).save(*args, **kwargs)


class Bill(models.Model):

    id = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=100, blank=False)
    payer = models.ForeignKey(SplititUser, on_delete=models.CASCADE, db_index=True)
    group = models.ForeignKey(SplititGroup, on_delete=models.CASCADE, db_index=True)

    SPLITTING_TYPE = (
        ("P", "PERCENTAGE"),
        ("FA", "FIXED_AMOUNT"),
        ("E", "EQUALLY"),
    )

    splitting_type = models.CharField(
        max_length=50, choices=SPLITTING_TYPE, default="E")
    total_amount = models.DecimalField(
        max_digits=7, decimal_places=1, default=0, blank=True)
    currency = models.CharField(max_length=100, blank=True, default="INR")
    created_date = models.DateTimeField(null=True, blank=True)
    modified_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Bill"
        verbose_name_plural = "Bill"

    def save(self, *args, **kwargs):

        if self.id == None or self.id == "":
            self.created_date = timezone.now()
            self.modified_date = timezone.now()
            self.id = str(uuid.uuid4())
        else:
            self.modified_date = timezone.now()

        super(Bill, self).save(*args, **kwargs)


class Transaction(models.Model):

    id = models.CharField(max_length=200, primary_key=True)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, db_index=True)
    debtor = models.ForeignKey(SplititUser, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=7, decimal_places=1, default=0, blank=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transaction"

    def get_payer(self):
        return str(self.bill.payer.username)

    def get_group(self):
        return str(self.bill.group.id)

    def save(self, *args, **kwargs):

        if self.id == None or self.id == "":
            self.id = str(uuid.uuid4())

        super(Transaction, self).save(*args, **kwargs)


class GroupTransaction(models.Model):

    id = models.CharField(max_length=200, primary_key=True)
    group = models.ForeignKey(SplititGroup, on_delete=models.CASCADE, db_index=True)
    payer = models.ForeignKey(
        SplititUser, related_name='transaction_payer', on_delete=models.CASCADE, db_index=True)
    debtor = models.ForeignKey(
        SplititUser, related_name='transaction_debtor', on_delete=models.CASCADE, db_index=True)
    amount = models.DecimalField(
        max_digits=7, decimal_places=1, default=0, blank=True)

    class Meta:
        verbose_name = "GroupTransaction"
        verbose_name_plural = "GroupTransaction"

    def save(self, *args, **kwargs):

        if self.id == None or self.id == "":
            self.id = str(uuid.uuid4())

        super(GroupTransaction, self).save(*args, **kwargs)
