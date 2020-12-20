from django.shortcuts import render
from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponseRedirect

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny

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
                response["status"] = 200
            else:
                response["status"] = 409

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error("SignUpAPI: %s at %s", e, str(exc_tb.tb_lineno))

        return Response(data=response, status=resp_status)
