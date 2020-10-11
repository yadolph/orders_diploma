from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from market.models import User, Product, ProductInfo, ProductParameter, Shop, Category, Parameter
from market.serializers import ProductSerializer, ProductCardSerializer
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
import yaml


class ProductView(APIView):

    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', 1)
        queryset = Product.objects.all()
        paginator = Paginator(queryset, 5)
        queryset = paginator.get_page(page)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)


class SingleProductView(APIView):

    def get(self, request, pk, *args, **kwargs):
        product = Product.objects.get(id=pk)
        serializer = ProductCardSerializer(product, many=False)
        return Response(serializer.data)


class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """

    def get(self, request, *args, **kwargs):
        return HttpResponse('Use POST bro')

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        data = request.POST['data']
        print(f'!!!! TYPE TYPE TYPE {type(data)}')
        data = yaml.load(request.POST['data'], Loader=yaml.FullLoader)
        print(data)

        shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)
        for category in data['categories']:
            category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
            category_object.shops.add(shop.id)
            category_object.save()
        ProductInfo.objects.filter(shop_id=shop.id).delete()
        for item in data['goods']:
            product, _ = Product.objects.get_or_create(name=item['name'],
                                                       category_id=item['category'],
                                                       shop_id=shop.id)

            product_info = ProductInfo.objects.create(product_id=product.id,
                                                      external_id=item['id'],
                                                      model=item['model'],
                                                      price=item['price'],
                                                      price_rrc=item['price_rrc'],
                                                      quantity=item['quantity'],
                                                      shop_id=shop.id)
            for name, value in item['parameters'].items():
                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(product_info_id=product_info.id,
                                                parameter_id=parameter_object.id,
                                                value=value)

        return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class SignIn(APIView):

    def get(self, request, *args, **kwargs):
        return HttpResponse('Use POST bro')

    def post(self, request):
        username = request.POST['username']
        print(username)

        password = request.POST['password']
        print(password)
        user = authenticate(request, username=username, password=password)
        print(authenticate(request, username=username, password=password))
        if user is not None:
            login(request, user)
            return JsonResponse({'Status': True, 'Message': f'Вы залогинились как {user.username}'})
        else:
            return JsonResponse({'Status': False, 'Errors': 'Вы не залогинились'})


class SignUp(APIView):

    def get(self, request, *args, **kwargs):
        return HttpResponse('Use POST bro')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create_user(username=username, email=username, password=password, is_active=True)
        user.save()
        return JsonResponse({'Status': True, 'Message': f'Создан пользователь {user.username} с id {user.id}'})


class LogOut(APIView):

    def get(self, request):
        logout(request)
        return JsonResponse({'Status': True, 'Message': 'Logout Success'})


class CheckUser(APIView):

    def get(self, request):
        print(request.user.username)
        return JsonResponse({'Message': f'Вы зашли как {request.user.username} с id {request.user.id}'})