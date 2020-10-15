from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from market.models import User, Product, ProductInfo, ProductParameter, Shop, Category, Parameter, Order, OrderItem
from market.serializers import ProductSerializer, ProductCardSerializer, OrderSerializer
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
import yaml
import json


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
        cart = request.session.get('cart', {})
        product = Product.objects.get(id=pk)

        if request.GET.get('add_to_cart', False):
            print(cart)
            if str(pk) in cart.keys():
                return JsonResponse({'Status': False, 'Error': 'Данный товар уже в корзине'})

            quantity = int(request.GET.get('quantity', 1))
            cart[pk] = quantity
            request.session['cart'] = cart
            request.session.modified = True
            if request.user.is_authenticated:
                request.user.cart = json.dumps(cart)
                request.user.save()

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

        data = yaml.load(request.POST['data'], Loader=yaml.FullLoader)

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
        #  Ошибки ?


class CartView(APIView):

    def assemble_cart(self,request):
        response = []
        cart = request.session.get('cart', False)
        total = 0
        print(cart)
        if cart:
            for id, quantity in cart.items():
                id, quantity = int(id), int(quantity)
                product = Product.objects.get(id=id)
                product_info = product.product_infos.get()
                shop = product.shop
                response.append({'id': id,
                                 'name': product.name,
                                 'quantity': quantity,
                                 'price': product_info.price,
                                 'subtotal': product_info.price * quantity,
                                 'shop': {'id': shop.id, 'name': shop.name}
                                 })
                total += product_info.price * quantity
            response.append({'total': total})
            return JsonResponse(response, safe=False)
        else:
            return JsonResponse({'Status': False, 'Error': 'Ваша корзина пуста'})


    def get(self, request, *args, **kwargs):
        return self.assemble_cart(request)

    def post(self,request, *args, **kwargs):
        id = request.POST.get('id')
        quantity = int(request.POST.get('quantity'))
        cart = request.session.get('cart', False)

        if not cart:
            return JsonResponse({'Status': False, 'Error': 'Ваша корзина пуста'})

        print(cart)
        print(id)

        if not id or not quantity:
            return JsonResponse({'Status': False, 'Error': 'Неверно переданы данные в запросе'})

        if id not in cart:
            return JsonResponse({'Status': False, 'Error': 'Товар с данным id отсутствует в корзине'})

        if id and quantity >= 0:
            cart.pop(id)
            request.session['cart'] = cart
            request.session.modified = True
            return self.assemble_cart(request)

        if id and quantity:
            cart[id] = quantity
            request.session['cart'] = cart
            request.session.modified = True
            return self.assemble_cart(request)


class PlaceOrder(APIView):
    def get(self, request, *args, **kwargs):
        cart_viewer = CartView()
        return cart_viewer.assemble_cart(request)

    def post(self, request, *args, **kwargs):
        confirmation = request.POST.get('order', False)
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Пожалуйста, зарегистрируйтесь или авторизуйтесь'})
        if confirmation:
            cart = request.session.get('cart')
            if not cart:
                return JsonResponse({'Status': False, 'Error': 'Ваша корзина пуста'})
            contact, _ = user.contacts.get_or_create(user=user, city='Empty', street='Empty', phone='Empty')
            order = Order(user=user, state='new', contact=contact)
            order.save()

            #  Добавить возможность редактирования контактов

            for id, quantity in cart.items():
                id, quantity = int(id), int(quantity)
                product = Product.objects.get(id=id)
                product_info = product.product_infos.get()
                order_item = OrderItem(order=order, product=product, product_info=product_info, quantity=quantity)
                order_item.save()

            serializer = OrderSerializer(order)
            response_data = serializer.data
            response_data['Status'], response_data['Message'] = True, 'Ваш заказ создан'
            request.session['cart'] = {}
            return Response(response_data)



class SignIn(APIView):

    def get(self, request, *args, **kwargs):
        return HttpResponse('Use POST bro')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            session_cart = request.session.get('cart', False)
            user_cart = json.loads(user.cart)
            if session_cart:
                user.cart = json.dumps(session_cart)
            elif user_cart:
                request.session['cart'] = user_cart
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


class SignOut(APIView):

    def get(self, request):
        logout(request)
        return JsonResponse({'Status': True, 'Message': 'Logout Success'})


class CartClear(APIView):

    def get(self, request):
        cart = request.session.get('cart', {})

        if cart:
            cart = {}
            request.session['cart'] = cart
            request.session.modified = True
            return JsonResponse({'Status': True})

        return JsonResponse({'Status': False})


class CheckUser(APIView):

    def get(self, request):
        print(request.user.username)
        return JsonResponse({'Message': f'Вы зашли как {request.user.username} с id {request.user.id}'})