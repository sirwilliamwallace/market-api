from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render
from sqlite3 import IntegrityError
from django.http import JsonResponse
import json
from market.models import Customer


# Create your views here.
def register_customer(request):
    context = {}
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.create_user(data['username'], data['email'], data['password'],
                                            first_name=data['first_name'], last_name=data['last_name'])

            user = Customer(user=user, phone=data['phone'], address=data['address'])
            user.save()
            context['id'] = user.id
            res = JsonResponse(context, status=201, safe=False)
            return res
        except IntegrityError:
            context['message'] = 'Username already exists'
            res = JsonResponse(context, status=400, safe=False)
            return res
        except KeyError:
            context['message'] = 'Missing required fields'
            res = JsonResponse(context, status=400, safe=False)
            return res
        except Exception as e:
            context['message'] = str(e)
            res = JsonResponse(context, status=400, safe=False)
            return res
    else:
        context['message'] = 'Method not allowed'
        res = JsonResponse(context, status=405, safe=False)
        return res


def list_customers(request):
    context = {}
    query = request.GET.get('search')
    if query:
        qs = (
                Q(user__first_name__contains=query)
                | Q(user__last_name__contains=query)
                | Q(user__username__contains=query)
                | Q(address__contains=query)
        )
        customers = Customer.objects.filter(qs).distinct()
        if not customers:
            context['message'] = 'Customer not found'
            res = JsonResponse(context, status=404, safe=False)
            return res
        context['customers'] = [customer.jsonified() for customer in customers]
        res = JsonResponse(context, status=200, safe=False)
        return res
    else:
        customers = Customer.objects.all()
        context['customers'] = [customer.jsonified() for customer in customers]
        res = JsonResponse(context, status=200, safe=False)
        return res


def customer_detail(request, customer_id):
    context = {}
    if request.method != 'GET':
        context['message'] = 'Invalid request method'
        res = JsonResponse(context, status=400, safe=False)
        return res
    else:
        try:
            product = Customer.objects.get(pk=customer_id)
            if product is None:
                context['message'] = 'Customer not found'
                res = JsonResponse(context, status=404, safe=False)
                return res
            context['customers'] = product.jsonified()
            res = JsonResponse(context['customers'], status=200, safe=False)
            return res
        except Customer.DoesNotExist as e:
            context['message'] = 'Customer not found'
            res = JsonResponse(context, status=404, safe=False)
            return res

# TODO: customer details, customer edit, login and logout, view customer profile
