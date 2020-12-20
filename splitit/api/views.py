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

            first_name = data["first_name"]
            last_name = data["last_name"]
            email = data["email"]
            password = data["password"]
            amount_owed = 0

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
                            members__username=request.user.username)

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


class SettleBalanceAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        response = {}
        resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        try:
            data = request.data
            logger.info("SettleBalanceAPI: %s", str(data))
            if not isinstance(data, dict):
                data = json.loads(data)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SettleBalanceAPI: %s at %s",
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

SettleBalance = SettleBalanceAPI.as_view()
