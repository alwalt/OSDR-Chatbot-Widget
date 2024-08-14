from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# import requests
from .langchain import chat


@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        # Directly pass the request to the langchain chat function
        response = chat(request)
        return response
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

