from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from easy_pdf.rendering import render_to_pdf_response


def getanswers(request):
    print('intczdcvs get')
    if request.is_ajax():
        import json
        data = ['Mow Lawn', 'Buy Groceries',]
        return HttpResponse(json.dumps(data), content_type="application/json")
    return 0