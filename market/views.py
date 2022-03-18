"""
    You can define utility functions here if needed
    For example, a function to create a JsonResponse
    with a specified status code or a message, etc.

    DO NOT FORGET to complete url patterns in market/urls.py
"""
import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Product


def product_insert(request):
    context = {}
    if request.method != 'POST':
        context['message'] = 'Invalid request method'
        res = JsonResponse(context, status=400, safe=False)
        return res
    elif request.body is not None:
        print(request.body)
        try:
            unicode_body = request.body.decode()
            data = json.loads(unicode_body)
            print(data)
            code = data.get('code')
            name = data.get('name')
            price = data.get('price')
            inventory = data.get('inventory', 0)
            if code is None or name is None or price is None:
                context['message'] = 'Invalid data received one of required fields is missing'
                res = JsonResponse(context, status=400, safe=False)
                return res
            elif inventory is not None:
                # if product exists, raise error
                if Product.objects.filter(code=code).exists():
                    context['message'] = 'Product already exists with code {}'.format(code)
                    res = JsonResponse(context, status=400, safe=False)
                    return res
                # Save product with inventory
                product = Product(code=code, name=name, price=price, inventory=inventory)
                product.save()
                context['message'] = f"{product.id}"
                res = JsonResponse(context, status=201, safe=False)
                return res
            else:
                # Save product without inventory default value is 0
                product = Product(code=code, name=name, price=price)
                product.save()
                context['message'] = f"{product.id}"
                res = JsonResponse(context, status=201, safe=False)
                print(res)
                return res
            product.save()
            context['message'] = 'Product inserted successfully'
            res = JsonResponse(context, status=201, safe=False)
            return res
        except Exception as e:
            context['message'] = 'Invalid data received {}'.format(e)
            res = JsonResponse(context, status=400, safe=False)
            return res

    else:
        # DEBUG
        res = JsonResponse(context, status=400, safe=False)
        context['message'] = f'Invalid data received {res} '
        print(res)
        return res


def product_list(request):
    context = {}
    if request.method != 'GET':
        context['message'] = 'Invalid request method'
        res = JsonResponse(context, status=400, safe=False)
        return res
    else:
        products = Product.objects.all()

        context['products'] = [product.jsonified() for product in products]
        res = JsonResponse(context, status=200, safe=False)
        return res
# TODO: Implement product_list and search_product and product_detail and product_update and product_delete
