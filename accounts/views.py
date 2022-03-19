from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render
from sqlite3 import IntegrityError
from django.http import JsonResponse
import json
from market.models import Customer
from django.contrib.auth import authenticate, login, logout


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


def customer_edit(request, customer_id):
    context = {}
    if request.method != 'POST':
        context['message'] = 'Invalid request method'
        res = JsonResponse(context, status=400, safe=False)
        return res
    else:
        try:
            customer = Customer.objects.get(pk=customer_id)
            if customer is None:
                context['message'] = 'Customer not found'
                res = JsonResponse(context, status=404, safe=False)
                return res
            data = json.loads(request.body)
            if data.get('id') or data.get('username') or data.get('password'):
                context["message"] = "Cannot edit customer's identity and credentials."
                res = JsonResponse(context, status=403, safe=False)
                return res
            # if data  is non its ok
            for key, value in data.items():
                if key == 'phone':
                    customer.phone = value
                elif key == 'address':
                    customer.address = value
                elif key == 'first_name':
                    customer.user.first_name = value
                elif key == 'last_name':
                    customer.user.last_name = value
                elif key == 'email':
                    customer.user.email = value
            customer.save()
            context['customers'] = customer.jsonified()
            res = JsonResponse(context['customers'], status=200, safe=False)
            return res
        except Customer.DoesNotExist as e:
            context['message'] = 'Customer not found'
            res = JsonResponse(context, status=404, safe=False)
            return res
        except ValueError as e:
            context['message'] = 'Invalid data received'
            res = JsonResponse(context, status=400, safe=False)
            return res
        except Exception as e:
            context['message'] = str(e)
            res = JsonResponse(context, status=400, safe=False)
            return res


def login_customer(request):
    if request.method != 'POST':
        context = {'message': 'Invalid request method'}
        res = JsonResponse(context, status=400, safe=False)
        return res
    else:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        if username is None or password is None:
            context = {'message': 'Invalid data received'}
            res = JsonResponse(context, status=400, safe=False)
            return res
        user = authenticate(username=username, password=password)
        if user is None:
            context = {'message': 'Username or Password is incorrect.'}
            res = JsonResponse(context, status=404, safe=False)
            return res
        else:
            login(request, user)
            context = {'message': 'You are logged in successfully.'}
            res = JsonResponse(context, status=200, safe=False)
            return res


def logout_customer(request):
    if request.method != 'POST':
        context = {'message': 'Invalid request method'}
        res = JsonResponse(context, status=400, safe=False)
        return res
    else:
        if request.user.is_authenticated:
            logout(request)
            context = {'message': 'You are logged out successfully.'}
            res = JsonResponse(context, status=200, safe=False)
            return res
        else:
            context = {'message': 'You are not logged in.'}
            res = JsonResponse(context, status=403, safe=False)
            return res


def customer_profile(request):
    if request.method != 'GET':
        context = {'message': 'Invalid request method'}
        res = JsonResponse(context, status=400, safe=False)
        return res
    else:
        if request.user.is_authenticated:
            customer = Customer.objects.get(user=request.user)
            context = {'customer': customer.jsonified()}
            res = JsonResponse(context['customer'], status=200, safe=False)
            return res
        else:
            context = {'message': 'You are not logged in.'}
            res = JsonResponse(context, status=403, safe=False)
            return res
# TODO: view customer profile
