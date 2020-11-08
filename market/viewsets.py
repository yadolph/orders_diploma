from rest_framework import viewsets
from market.models import Shop, Category
from market.serializers import ShopSerializerShort, CategorySerializer, ShopSerializer


class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializerShort

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ShopSerializer
        else:
            return ShopSerializerShort


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


