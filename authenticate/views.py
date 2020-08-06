from django.shortcuts import render


def template(request):
    return render(request, 'index.html')
