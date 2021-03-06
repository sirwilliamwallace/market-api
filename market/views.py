"""
    You can define utility functions here if needed
    For example, a function to create a JsonResponse
    with a specified status code or a message, etc.

    DO NOT FORGET to complete url patterns in market/urls.py
"""
import json
from sqlite3 import IntegrityError

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, get_list_or_404
from .models import Product, Order, OrderRow


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
    elif request.GET.get('search'):
        search = request.GET['search']
        products = Product.objects.filter(name__icontains=search)
        context['products'] = [product.jsonified() for product in products]
        res = JsonResponse(context, status=200, safe=False)
        return res
    else:
        products = Product.objects.all()

        context['products'] = [product.jsonified() for product in products]
        res = JsonResponse(context, status=200, safe=False)
        return res


def product_detail(request, product_id):
    context = {}
    if request.method != 'GET':
        context['message'] = 'Invalid request method'
        res = JsonResponse(context, status=400, safe=False)
        return res
    else:
        try:
            product = Product.objects.get(pk=product_id)
            if product is None:
                context['message'] = 'Product not found'
                res = JsonResponse(context, status=404, safe=False)
                return res
            context['product'] = product.jsonified()
            res = JsonResponse(context['product'], status=200, safe=False)
            return res
        except Product.DoesNotExist as e:
            context['message'] = 'Product not found'
            res = JsonResponse(context, status=404, safe=False)
            return res


def edit_inventory(request, product_id):
    context = {}
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist as e:
        context['message'] = 'Product not found'
        res = JsonResponse(context, status=404, safe=False)
        return res
    if request.method != 'POST':
        context["message"] = "Invalid request method"
        res = JsonResponse(context, status=400, safe=False)
        return res
    try:
        data = json.loads(request.body.decode('utf-8'))
        inventory = int(data.get('amount'))
        print(inventory < 0)
        if inventory is None:
            context['message'] = 'None inventory value received'
            res = JsonResponse(context, status=400, safe=False)
            return res
        elif inventory < 0:
            product.decrease_inventory(inventory * -1)
            context['product'] = product.jsonified()
            res = JsonResponse(context['product'], status=200, safe=False)
            return res
        elif inventory > 0:
            product.increase_inventory(inventory)
            context['product'] = product.jsonified()
            res = JsonResponse(context['product'], status=200, safe=False)
            return res
        else:
            context['message'] = 'Invalid inventory value'
            res = JsonResponse(context, status=400, safe=False)
            return res
    except ValueError as e:
        context['message'] = f'Invalid data received {e}'
        res = JsonResponse(context, status=400, safe=False)
        return res


def shopping_cart(request):
    context = {}
    if request.method != 'GET':
        context['message'] = 'Invalid request method'
        res = JsonResponse(context, status=400, safe=False)
        return res
    if request.user.is_authenticated and request.user.is_active:
        order = Order.initiate(request.user.customer)
        context = order.jsonified()
        res = JsonResponse(context, status=200, safe=False)
        return res
    else:
        context['message'] = 'You are not logged in.'
        res = JsonResponse(context, status=403, safe=False)
        return res


def add_to_cart(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Wrong method.'}, status=404, safe=False)
    try:
        if request.user.is_authenticated and request.user.is_active:
            data = json.loads(request.body)
            order = Order.initiate(request.user.customer)
            errors = []
            for item in data:
                try:
                    if Product.objects.filter(code=item['code']).exists():
                        product = Product.objects.get(code=item.get('code'))
                        amount = int(item.get('amount'))
                        order.add_product(product, amount)
                except Exception as e:
                    errors.append({'code': item['code'], 'message': str(e)})
            if errors:
                context = {'errors': errors}
                res = JsonResponse(context, status=400, safe=False)
                return res
            context = order.jsonified()
            res = JsonResponse(context, status=200, safe=False)
            return res
        else:
            context = {'message': 'You are not logged in.'}
            res = JsonResponse(context, status=403, safe=False)
            return res
    except Exception as e:
        context = {'message': str(e)}
        res = JsonResponse(context, status=404)
        return res


def remove_from_cart(request):
    context = {}
    if request.method != 'POST':
        return JsonResponse({'message': 'Wrong Method'}, status=404)
    try:
        if request.user.is_authenticated and request.user.is_active:
            data = json.loads(request.body)
            order = Order.initiate(request.user.customer)
            errors = []
            for item in data:
                try:
                    if Product.objects.filter(code=item.get('code')).exists():
                        if 'amount' not in item:
                            item['amount'] = None
                        product = Product.objects.get(code=item.get('code'))
                        amount = item.get('amount')
                        try:
                            order.remove_product(product, amount)
                        except OrderRow.DoesNotExist as e:
                            errors.append({'code': item['code'], 'message': 'Does not exist in cart'})
                except Exception as e:
                    errors.append({'code': item['code'], 'message': str(e)})
            if errors:
                context = {'errors': errors}
                res = JsonResponse(context, status=400, safe=False)
                return res
            else:
                context = order.jsonified()
                res = JsonResponse(context, status=400)
                return res
        else:
            context['message'] = 'You are not logged in.'
            res = JsonResponse(context, status=403)
            return res
    except Exception as e:
        context['message'] = str(e)
        res = JsonResponse(context, status=400)
        return res


def submit_cart(request):
    context = {}
    if request.method != 'POST':
        context['message'] = 'Wrong method'
        res = JsonResponse(context, status=404, safe=False)
        return res
    try:
        if request.user.is_authenticated and request.user.is_active:

            data = json.loads(request.body)
            order = Order.initiate(request.user.customer)
            try:
                order.submit()
            except Exception as e:
                context['message'] = str(e)
                res = JsonResponse(context, status=400, safe=False)
                return res
            context = order.jsonified()
            res = JsonResponse(context['items'], status=200, safe=False)
            return res
        else:
            context['message'] = 'You are not logged in.'
            res = JsonResponse(context, status=403, safe=False)
            return res
    except Exception as e:
        context['message'] = str(e)
        res = JsonResponse(context, status=400, safe=False)
        return res