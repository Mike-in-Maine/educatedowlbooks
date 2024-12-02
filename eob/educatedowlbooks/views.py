from django.shortcuts import render

def home(request):
    context={}
    return render(request, "index.html", context=context)

def hello(request):
    return render(request, "hello.html")


