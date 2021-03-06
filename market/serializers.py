from rest_framework import serializers
from market.models import Shop, Category, Product, ProductInfo, \
    ProductParameter, Parameter, User, Order, OrderItem, Contact


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ('name',)


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)


class ProductInfoSerializer(serializers.ModelSerializer):
    product_parameters = ProductParameterSerializer(many=True)
    shop = serializers.StringRelatedField()

    class Meta:
        model = ProductInfo
        fields = ('shop', 'quantity', 'price', 'price_rrc', 'product_parameters')


class ProductInfoShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductInfo
        fields = ('price',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ShopSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Shop
        fields = ('name', 'categories', 'products', 'owner')


class ShopSerializerShort(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = ('name', 'id')


class ProductSerializer(serializers.ModelSerializer):
    shop = ShopSerializerShort()
    category = CategorySerializer()
    product_infos = ProductInfoShortSerializer(read_only=True, many=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'shop', 'category', 'product_infos')


class ProductCardSerializer(serializers.ModelSerializer):
    shop = ShopSerializerShort()
    category = CategorySerializer()
    product_infos = ProductInfoSerializer(read_only=True, many=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'shop', 'category', 'product_infos')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'company', 'position', 'type', 'password')


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta():
        model = OrderItem
        fields = ('order', 'product', 'quantity')


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemSerializer(read_only=True, many=True)
    contact = ContactSerializer()
    class Meta:
        model = Order
        fields = ('id', 'user', 'state', 'ordered_items', 'dt', 'contact')
