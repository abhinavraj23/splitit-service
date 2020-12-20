from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from rest_framework_simplejwt import views as jwt_views

from . import views

urlpatterns = [
    url(r'^token/$',
        jwt_views.TokenObtainPairView.as_view(),
        name='token_obtain_pair'),
    url(r'^token/refresh/$',
        jwt_views.TokenRefreshView.as_view(),
        name='token_refresh'),

    url(r'^sign-up/$', views.SignUp),
    url(r'^create-group/$', views.CreateGroup),

    url(r'^add-member-to-group/$', views.AddMemberToGroup),
    url(r'^remove-member-from-group/$', views.RemoveMemberFromGroup),

    url(r'^create-bill/$', views.CreateBill),
    url(r'^update-bill/$', views.UpdateBill),

    url(r'^get-total-debt/$', views.GetTotalDebt),
    url(r'^get-group-debt/$', views.GetGroupDebt),

    url(r'^settle-transaction/$', views.SettleTransaction)
]
