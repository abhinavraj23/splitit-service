from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from rest_framework_simplejwt import views as jwt_views

from . import views

urlpatterns = [
    url(r'^token/',
        jwt_views.TokenObtainPairView.as_view(),
        name='token_obtain_pair'),
    url(r'^token/refresh/',
        jwt_views.TokenRefreshView.as_view(),
        name='token_refresh'),

]
