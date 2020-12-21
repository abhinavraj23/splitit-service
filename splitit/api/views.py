from django.shortcuts import render
from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponseRedirect

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated

from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from datetime import datetime

from api.models import *
from api.utils import *

import sys
import logging
import json
import requests
import hashlib
import threading
import math
import random

logger = logging.getLogger(__name__)


class SignUpAPI(APIView):

    def post(self, request, *args, **kwargs):
        response = {}
        resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        try:
            data = request.data
            logger.info("SignUpAPI: %s", str(data))
            if not isinstance(data, dict):
                data = json.loads(data)

            first_name = data.get("first_name")
            last_name = data.get("last_name", '')
            email = data.get("email")
            password = data.get("password")
            amount_owed = 0

            if isNull(first_name) or isNull(email) or isNull(password):
                resp_status = status.HTTP_400_BAD_REQUEST
            else:
                if SplititUser.objects.filter(username=email).exists() == False:
                    splitit_user_obj = SplititUser.objects.create(
                        username=email, first_name=first_name, last_name=last_name, email=email, amount_owed=amount_owed)
                    splitit_user_obj.set_password(password)
                    splitit_user_obj.save()
                    response["username"] = splitit_user_obj.username
                    resp_status = status.HTTP_200_OK
                else:
                    resp_status = status.HTTP_409_CONFLICT

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SignUpAPI: %s at %s", e, str(exc_tb.tb_lineno))

        return Response(data=response, status=resp_status)


class CreateGroupAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        response = {}
        resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        try:
            data = request.data
            logger.info("CreateGroupAPI: %s", str(data))
            if not isinstance(data, dict):
                data = json.loads(data)

            name = data.get("name")
            description = data.get("description", "")
            to_simplify = data.get("to_simplify", False)
            to_simplify = bool(to_simplify)

            created_by_obj = SplititUser.objects.get(
                username=request.user.username)

            if name is None:
                resp_status = status.HTTP_400_BAD_REQUEST
            else:
                splitit_group_obj = SplititGroup.objects.create(
                    name=name, description=description, to_simplify=to_simplify, created_by=created_by_obj)

                splitit_group_obj.members.add(created_by_obj)
                splitit_group_obj.save()
                resp_status = status.HTTP_200_OK

                # if SplititGroup.objects.filter(created_by=created_by_obj, name=name).exists() == False:
                #     splitit_group_obj = SplititGroup.objects.create(
                #         name=name, description=description, to_simplify=to_simplify, created_by=created_by_obj)

                #     splitit_group_obj.members.add(created_by_obj)
                #     splitit_group_obj.save()

                # else:
                #     response["message"] = "USER CANNOT HAVE TWO GROUPS OF SAME NAME"
                #     esp_status = status.HTTP_409_CONFLICT

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateGroupAPI: %s at %s", e, str(exc_tb.tb_lineno))

        return Response(data=response, status=resp_status)


class AddMemberToGroupAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        response = {}
        resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        try:
            data = request.data
            logger.info("AddMemberToGroupAPI: %s", str(data))
            if not isinstance(data, dict):
                data = json.loads(data)

            group_id = data.get('group_id')
            username = data.get('username')

            if isNull(group_id) or isNull(username):
                resp_status = status.HTTP_400_BAD_REQUEST
            else:
                group_exists = SplititGroup.objects.filter(
                    pk=group_id).exists()
                user_exists = SplititUser.objects.filter(
                    username=username).exists()

                if group_exists and user_exists:
                    splitit_group_obj = SplititGroup.objects.get(pk=group_id)

                    if request.user.username != splitit_group_obj.created_by.username:
                        resp_status = status.HTTP_401_UNAUTHORIZED
                    else:
                        user_already_member = SplititGroup.objects.filter(
                            members__username=request.user.username).exists()

                        if user_already_member:
                            resp_status = status.HTTP_409_CONFLICT
                        else:
                            splitit_user_obj = SplititUser.objects.get(
                                username=username)
                            splitit_group_obj.members.add(splitit_user_obj)
                            splitit_group_obj.save()
                            resp_status = status.HTTP_200_OK
                else:
                    resp_status = status.HTTP_400_BAD_REQUEST

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("AddMemberToGroupAPI: %s at %s",
                         e, str(exc_tb.tb_lineno))

        return Response(data=response, status=resp_status)


class RemoveMemberFromGroupAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        response = {}
        resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        try:
            data = request.data
            logger.info("RemoveMemberFromGroupAPI: %s", str(data))
            if not isinstance(data, dict):
                data = json.loads(data)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("RemoveMemberFromGroupAPI: %s at %s",
                         e, str(exc_tb.tb_lineno))

        return Response(data=response, status=resp_status)


class CreateBillAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        response = {}
        resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        try:
            data = request.data
            logger.info("CreateBillAPI: %s", str(data))
            if not isinstance(data, dict):
                data = json.loads(data)

            created_by_obj = SplititUser.objects.get(
                username=request.user.username)

            name = data.get('name')
            group_id = data.get('group_id')
            splitting_type = data.get('splitting_type')
            currency = data.get('currency', 'INR')

            member_transactions = data.get('member_transactions')

            '''
            The members transaction data according to splitting method is expected
            to be calculated in the frontend and is expected in the following format:

            [
                {
                    user_id: "a1",
                    amount: "90"
                },
                {
                    user_id: "a2",
                    amount: "100"
                },
                ...
            ]
            '''

            total_amount = data.get('total_amount')

            if isNull(group_id) or isNull(splitting_type) or isNull(member_transactions) or isNull(total_amount) or isNull(name):
                resp_status = status.HTTP_400_BAD_REQUEST

            else:
                payer_obj = SplititUser.objects.get(
                    username=request.user.username)

                total_amount = float(total_amount)
                payer_obj.amount_paid += total_amount
                payer_obj.save()

                group_obj = SplititGroup.objects.get(pk=group_id)

                if Bill.objects.filter(group=group_obj, name=name).exists() == False:
                    bill_obj = Bill.objects.create(
                        payer=payer_obj, name=name, group=group_obj, splitting_type=splitting_type, total_amount=total_amount, currency=currency)

                    response['bill_id'] = str(bill_obj.id)

                    '''
                    Below is an important logic of the program, for each debtor, this logic will

                    1) Add the amount_owed to the debtor
                    2) Add the transaction to the transaction table
                    3) Add the transaction to group transaction table
                    '''

                    for member_transaction in member_transactions:
                        debtor_id = member_transactions['user_id']
                        debtor_obj = SplititUser.objects.get(id=debtor_id)
                        amount = float(member_transactions['amount'])

                        debtor_obj.amount_owed += amount
                        debtor_obj.save()

                        payer_obj = bill_obj.payer
                        group_obj = bill_obj.group

                        addToGroupTransactions(
                            amount, payer_obj, debtor_obj, group_obj)
                        Transaction.objects.create(
                            bill=bill_obj, amount=amount, debtor=debtor_obj)

                    resp_status = status.HTTP_200_OK
                else:
                    response["message"] = "GROUP CANNOT HAVE TWO BILLS OF SAME NAME"
                    resp_status = status.HTTP_409_CONFLICT

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("CreateBillAPI: %s at %s",
                         e, str(exc_tb.tb_lineno))

        return Response(data=response, status=resp_status)


class UpdateBillAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        response = {}
        resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        try:
            data = request.data
            logger.info("UpdateBillAPI: %s", str(data))
            if not isinstance(data, dict):
                data = json.loads(data)

            '''
            This API assumes that payer cannot change, group cannot be changed,
            name of the bill can be changed, currency can be changed, total amount can be changed,
            and the member transactions have to passed again in the same format i.e.

            [
                {
                    user_id: "a1",
                    amount: "90"
                },
                {
                    user_id: "a2",
                    amount: "100"
                },
                ...
            ]

            Also only the payer can update the bill
            '''

            bill_id = data.get("bill_id")
            bill_obj = Bill.objects.get(id=bill_id)

            if bill_obj.payer.username != request.user.username:
                resp_status = status.HTTP_401_UNAUTHORIZED
            else:
                name = data.get('name')

                splitting_type = data.get('splitting_type')
                currency = data.get('currency', 'INR')

                member_transactions = data.get('member_transactions')

                total_amount = data.get('total_amount')

                if isNull(splitting_type) or isNull(member_transactions) or isNull(total_amount) or isNull(name):
                    resp_status = status.HTTP_400_BAD_REQUEST

                else:

                    group_obj = bill_obj.group

                    if Bill.objects.filter(group=group_obj, name=name).exists() == True:
                        response["message"] = "GROUP CANNOT HAVE TWO BILLS OF SAME NAME"
                        resp_status = status.HTTP_409_CONFLICT

                    else:
                        # Delete the transaction of the previous bill
                        previous_transaction_objs = Transaction.objects.filter(
                            bill=bill_obj)
                        payer_obj = bill_obj.payer

                        for transaction_obj in previous_transaction_objs:
                            debtor_obj = transaction_obj.debtor
                            amount = transaction_obj.amount
                            debtor_obj.amount_owed -= amount
                            debtor_obj.save()
                            addToGroupTransactions(
                                amount, debtor_obj, payer_obj, group_obj)
                            transaction_obj.delete()

                        previous_amount = bill_obj.total_amount

                        payer_obj.amount_paid += total_amount - previous_amount
                        payer_obj.save()

                        bill_obj.name = name
                        bill_obj.splitting_type = splitting_type
                        bill_obj.currency = currency
                        bill_obj.total_amount = total_amount
                        bill_obj.save()

                        # Now update the Transaction and Group transaction table
                        for member_transaction in member_transactions:
                            debtor_id = member_transactions['user_id']
                            debtor_obj = SplititUser.objects.get(id=debtor_id)
                            amount = float(member_transactions['amount'])

                            debtor_obj.amount_owed += amount
                            debtor_obj.save()

                            addToGroupTransactions(
                                amount, payer_obj, debtor_obj, group_obj)
                            Transaction.objects.create(
                                bill=bill_obj, amount=amount, debtor=debtor_obj)

                        response['id'] = str(bill_obj.id)
                        resp_status = status.HTTP_200_OK

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdateBillAPI: %s at %s",
                         e, str(exc_tb.tb_lineno))

        return Response(data=response, status=resp_status)


class GetTotalDebtAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        response = {}
        resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        try:
            data = request.data
            logger.info("GetTotalDebtAPI: %s", str(data))
            if not isinstance(data, dict):
                data = json.loads(data)

            splitit_user_obj = SplititUser.objects.get(
                username=request.user.username)
            response['total_amount_owed'] = splitit_user_obj.amount_owed
            response['total_amount_paid'] = splitit_user_obj.amount_paid
            resp_status = status.HTTP_200_OK

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetTotalDebtAPI: %s at %s",
                         e, str(exc_tb.tb_lineno))

        return Response(data=response, status=resp_status)


class GetGroupDebtAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        response = {}
        resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        try:
            data = request.data
            logger.info("GetGroupDebtAPI: %s", str(data))
            if not isinstance(data, dict):
                data = json.loads(data)

            group_id = data.get('group_id')

            if isNull(group_id):
                resp_status = status.HTTP_400_BAD_REQUEST

            else:
                group_obj = SplititGroup.objects.get(id=group_id)
                user_obj = SplititUser.objects.get(
                    username=request.user.username)
                group_transaction_objs = GroupTransaction.objects.filter(
                    group=group_obj, debtor=user_obj)

                amount_owed = 0
                for group_transaction_obj in group_transaction_objs:
                    amount_owed += group_transaction_obj.amount

                group_transaction_objs = GroupTransaction.objects.filter(
                    group=group_obj, payer=user_obj)

                amount_paid = 0
                for group_transaction_obj in group_transaction_objs:
                    amount_paid += group_transaction_obj.amount

                response['group_amount_owed'] = amount_owed
                response['group_amount_paid'] = amount_paid
                resp_status = status.HTTP_200_OK

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("GetGroupDebtAPI: %s at %s",
                         e, str(exc_tb.tb_lineno))

        return Response(data=response, status=resp_status)


class SettleTransactionAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        response = {}
        resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        try:
            data = request.data
            logger.info("SettleTransactionAPI: %s", str(data))
            if not isinstance(data, dict):
                data = json.loads(data)

            group_id = data.get('group_id')

            if isNull(group_id):
                resp_status = status.HTTP_400_BAD_REQUEST
            else:
                group_obj = SplititGroup.objects.get(id=group_id)
                group_transaction_objs = GroupTransaction.objects.filter(
                    group=group_obj)

                if group_obj.to_simplify:
                    response['settlement'] = minimize_transaction(
                        group_transaction_objs)

                else:
                    '''
                    The result will of the  following format:

                    [
                        {
                            payer: user_id,
                            debtor: user_id,
                            amount: 100 (whatever)
                        }
                    ]
                    '''
                    settlement = []
                    for group_transaction_obj in group_transaction_objs:
                        temp = {}
                        temp['payer'] = str(group_transaction_obj.payer.id)
                        temp['debtor'] = str(group_transaction_obj.debtor.id)
                        temp['amount'] = str(group_transaction_obj.amount)
                        settlement.append(temp)

                    response['settelement'] = settlement
                resp_status = status.HTTP_200_OK

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SettleTransactionAPI: %s at %s",
                         e, str(exc_tb.tb_lineno))

        return Response(data=response, status=resp_status)


SignUp = SignUpAPI.as_view()

CreateGroup = CreateGroupAPI.as_view()

AddMemberToGroup = AddMemberToGroupAPI.as_view()

RemoveMemberFromGroup = RemoveMemberFromGroupAPI.as_view()

CreateBill = CreateBillAPI.as_view()

UpdateBill = UpdateBillAPI.as_view()

GetTotalDebt = GetTotalDebtAPI.as_view()

GetGroupDebt = GetGroupDebtAPI.as_view()

SettleTransaction = SettleTransactionAPI.as_view()
