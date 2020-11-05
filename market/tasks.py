from celery import shared_task
from django.core.mail import send_mail
from orders.settings import EMAIL_FROM

#Для теста работоспособности Celery - простая задача на сложение
@shared_task
def adding_task(x, y):
    return x + y

@shared_task
def email(subject, message, from_email, recipient_list):
    a = send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    if a:
        return 'success!'
    else:
        return 'nothing has been sent'



def update_partner_data(data):
    shop, _ = Shop.objects.get_or_create(name=data['shop'])
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