"""
    You can define utility functions here if needed
    For example, a function to create a JsonResponse
    with a specified status code or a message, etc.

    DO NOT FORGET to complete url patterns in market/urls.py
"""


def product_insert(request):
    # hint: you should check request method like below
    if request.method != 'POST':
        pass  # return appropriate error message
    pass  # main logic and return normal response
