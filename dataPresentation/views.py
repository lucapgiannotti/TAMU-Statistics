from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from .models import GPAData  # Assuming you have a model to fetch GPA data

def data_presentation_view(request):
    year = request.GET.get('year')
    term = request.GET.get('term')
    college = request.GET.get('college')
    
    # Fetch data based on the selected parameters
    gpa_data = GPAData.objects.filter(year=year, term=term, college=college)
    
    context = {
        'gpa_data': gpa_data,
        'year': year,
        'term': term,
        'college': college,
    }
    return render(request, 'dataPresentation/data_presentation.html', context)