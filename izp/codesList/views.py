from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from easy_pdf.rendering import render_to_pdf_response
from django.contrib.auth.decorators import login_required

def get_codes(num):
	dict = {}
	for x in range(1, num):
		dict[x] = 1000+x
	return dict

@login_required(login_url='/admin/')
def code_page_view(request):
	codes_dict = get_codes(42)
	return render(request, 'codesList/codeList.html', {"codes_dict" : codes_dict}) 

@login_required(login_url='/admin/')
def perform_pdf(request):
	codes_dict = get_codes(42)
	return render_to_pdf_response(request, 'codesList/codeList.html', {"codes_dict" : codes_dict}, filename="codes.pdf", encoding='utf-8')

