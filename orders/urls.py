from django.contrib import admin
from django.urls import path, include
from market.views import ProductView, PartnerUpdate, SignIn, SignUp, CheckUser, \
    SignOut, SingleProductView, CartView, CartClear, PlaceOrder, OrderList, ContactUpdate
from rest_framework.routers import DefaultRouter
from market import viewsets

router = DefaultRouter()
router.register('categories', viewsets.CategoryViewSet)
router.register('shops', viewsets.ShopViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ProductView.as_view()),
    path('', include(router.urls)),
    path('partner_update/', PartnerUpdate.as_view()),
    path('signin/', SignIn.as_view()),
    path('signup/', SignUp.as_view()),
    path('check/', CheckUser.as_view(), name='check_user'),
    path('signout/', SignOut.as_view()),
    path('product/<int:pk>', SingleProductView.as_view()),
    path('cart/', CartView.as_view()),
    path('cartclear/', CartClear.as_view()),
    path('place_order/', PlaceOrder.as_view()),
    path('order_list/', OrderList.as_view()),
    path('contacts/', ContactUpdate.as_view()),
]
