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

from splitit.api.models import *
from splitit.api.utils import *

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

            if group_id is None or username is None:
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
                resp_status = status.HTTP_401_UNAUTHORIZED

            else:
                payer_obj = SplititUser.objects.get(
                    username=request.user.username)
                group_obj = SplititGroup.objects.get(pk=group_id)

                if Bill.objects.filter(group=group_obj, name=name).exists() == False:
                    bill_obj = Bill.objects.create(
                        payer=payer_obj, name=name, group=group_obj, splitting_type=splitting_type, total_amount=total_amount, currency=currency)

                    response['bill_id'] = str(bill_obj.id)

                    '''
                    Below is an important logic of the program, for each debter, this logic will

                    1) Add the amount_owed to the debter
                    2) Add the transaction to the transaction table
                    3) Add the transaction to group transaction table
                    '''

                    for member_transaction in member_transactions:
                        debter_id = member_transactions['user_id']
                        debter_obj = SplititUser.objects.get(id=debter_id)
                        amount = float(member_transactions['amount'])

                        debter_obj.amount_owed += amount
                        debter_obj.save()

                        addToGroupTransactions(amount, debter_obj, bill_obj)
                        Transaction.objects.create(
                            bill=bill_obj, amount=amount, debter=debter_obj)

                else:
                    response["message"] = "GROUP CANNOT HAVE TWO BILLS OF SAME NAME"
                    esp_status = status.HTTP_409_CONFLICT

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

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("UpdateBillAPI: %s at %s",
                         e, str(exc_tb.tb_lineno))

        return Response(data=response, status=resp_status)


class GetTotalDebtAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        response = {}
        resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        try:
            data = request.data
            logger.info("GetTotalDebtAPI: %s", str(data))
            if not isinstance(data, dict):
                data = json.loads(data)

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
