from django.shortcuts import render


def home(request):
    return render(request, 'landing.html')

def blog(request):
    return render(request, 'notices_blog.html')
