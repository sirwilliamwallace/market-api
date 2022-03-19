from django.contrib.auth.models import User
from django.shortcuts import render
from sqlite3 import IntegrityError
from django.http import JsonResponse
import json
from .models import Profile


# Create your views here.
def register_user(request):
    context = {}
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.create_user(data['username'], data['email'], data['password'],
                                            first_name=data['first_name'], last_name=data['last_name'])

            user = Profile(user=user, phone=data['phone'], address=data['address'])
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
