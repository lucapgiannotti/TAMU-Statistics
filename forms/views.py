from django.shortcuts import render
from .forms import SubmissionForm

def form_view(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            # Process the form data
            year = form.cleaned_data['year']
            term = form.cleaned_data['term']
            college = form.cleaned_data['college']
            # Add your processing logic here
    else:
        form = SubmissionForm()
    return render(request, 'forms/form.html', {'form': form})