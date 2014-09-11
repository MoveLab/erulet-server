from django.shortcuts import render


def show_landing_page(request):
    context = {}
    return render(request, 'frontulet/landing_page.html', context)
