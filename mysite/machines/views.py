from django.shortcuts import render, redirect
from .models import Machine, Booking
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .forms import BookingForm  # Import the BookingForm from forms.py
from django.shortcuts import redirect, get_object_or_404
from django. contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.db.models import Q


@login_required
def machine_list(request):
    # machines = Machine.objects.all()
    # return render(request, 'machines/machine_list.html', {'machines': machines})

    # Get the search query from the request's GET parameters
    search_query = request.GET.get('search')

    # Query the machines based on the search query (case-insensitive search)
    machines = Machine.objects.filter(name__icontains=search_query) if search_query else Machine.objects.all()

    context = {
        'machines': machines,
    }
    return render(request, 'machines/machine_list.html', context)

@login_required
def machine_detail(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)

    # Check if the user is authenticated
    user_can_free = request.user.is_authenticated
    
    # Check if the user has an active booking for this machine
    user_active_booking = None
    if user_can_free:
        user_active_booking = Booking.objects.filter(machine=machine, user=request.user, end_time__gte=timezone.now()).first()
    context = {
        'machine': machine,
        'user_can_free': user_can_free,
        'user_has_active_booking': user_active_booking is not None,
        'user_active_booking': user_active_booking,
    }
    
    return render(request, 'machines/machine_detail.html', context)
    

@login_required
def book_machine(request, machine_id):
    machine = Machine.objects.get(pk=machine_id)
    booking_form = BookingForm()  # Create an instance of the form

    if request.method == 'POST':
        booking_form = BookingForm(request.POST)  # Populate the form with POST data
        if booking_form.is_valid():
            booking_duration = booking_form.cleaned_data['hours']
            start_time = timezone.now()
            end_time = start_time + timedelta(hours=booking_duration)
            purpose = booking_form.cleaned_data['purpose']
            machine.purpose = purpose  # Get the purpose from the form
            machine.start_time = start_time
            machine.end_time = end_time
            machine.status = False
            machine.user = request.user
            machine.save()
            return redirect('machine_list')
    
    return render(request, 'machines/book_machine.html', {'machine': machine, 'booking_form': booking_form})

@login_required
def unbook_machine(request, machine_id):
    machine = Machine.objects.get(pk=machine_id)
    # Check if the user has the authority to unbook this machine
    print("machine.user", machine.user, "and request.user", request.user)
    if machine.user == request.user:
        machine.status = True
        machine.user = None
        machine.save()
        messages.success(request, "You have successfully unbooked the machine.")
    else:
        messages.error(request, "You do not have permission to unbook this machine.")
    
    return render(request, 'unbook_machine.html', {'machine': machine, 'booking_form': unbook_machine})

def send_notification_email(user_email, machine_name):
    subject = 'Machine Booking Reminder'
    message = f'Dear User,\n\nYour booking for {machine_name} has ended. Please free the machine if you are done using it.'
    from_email = 'kartikeymahajan321@gmail.com'  # Use the same email configured in settings.py
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)
    

