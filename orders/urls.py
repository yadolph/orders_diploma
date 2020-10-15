"""orders URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from market.views import ProductView, PartnerUpdate, SignIn, SignUp, CheckUser, \
    SignOut, SingleProductView, CartView, CartClear, PlaceOrder

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ProductView.as_view()),
    path('partner_update/', PartnerUpdate.as_view()),
    path('signin/', SignIn.as_view()),
    path('signup/', SignUp.as_view()),
    path('check/', CheckUser.as_view()),
    path('signout/', SignOut.as_view()),
    path('product/<int:pk>', SingleProductView.as_view()),
    path('cart/', CartView.as_view()),
    path('cartclear/', CartClear.as_view()),
    path('place_order/', PlaceOrder.as_view()),
]
