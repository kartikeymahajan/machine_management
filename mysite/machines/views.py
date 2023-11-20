import time

from django.shortcuts import render, redirect
from .models import Machine, Booking, Notepad
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import BookingForm, NotepadForm  # Import the BookingForm from forms.py
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django. contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth.views import LogoutView
from datetime import timedelta
import requests

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
            days = booking_form.cleaned_data['days'] if type(booking_form.cleaned_data['days']) == int else 0
            hours = booking_form.cleaned_data['hours'] if type(booking_form.cleaned_data['hours'])==int else 0
            minutes = booking_form.cleaned_data['minutes'] if type(booking_form.cleaned_data['minutes'])==int else 0

            # Calculate booking_duration
            booking_duration = hours + (days * 24) + (minutes / 60)
            start_time = timezone.now()
            end_time = start_time + timedelta(hours=booking_duration)
            purpose = booking_form.cleaned_data['purpose']
            machine.purpose = purpose  # Get the purpose from the form
            machine.start_time = start_time
            machine.end_time = end_time
            machine.status = False
            machine.user = request.user
            machine.nz_start_time = start_time + timedelta(hours=7, minutes=30)
            machine.nz_end_time = end_time + timedelta(hours=7, minutes=30)

            # Create a new booking record
            Booking.objects.create(
                user=request.user,
                machine=machine,
                start_time=start_time,
                end_time=end_time,
                purpose = purpose, 
            )

            machine.save()
            print(machine.name, request.user, start_time, end_time)
            date_time = end_time.strftime("%m/%d/%Y, %H:%M:%S")
            send_slack_booking_notification(request.user, machine.name, date_time)

            return redirect('machine_list')
    
    return render(request, 'machines/book_machine.html', {'machine': machine, 'booking_form': booking_form})

@login_required
def unbook_machine(request, machine_id):
    machine = Machine.objects.get(pk=machine_id)
    # Check if the user has the authority to unbook this machine
    if machine.user == request.user:
        machine.status = True
        machine.user = None

        # deleting the record of VM from booking
        booking = Booking.objects.get(machine__name=machine.name)
        booking.delete()
        machine.save()
        send_slack_unbooking_notification(machine.name)

        messages.success(request, "You have successfully unbooked the machine.")
    else:
        messages.error(request, "You do not have permission to unbook this machine.")

    return render(request, 'unbook_machine.html', {'machine': machine, 'booking_form': unbook_machine})


@login_required
def edit_notepad(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    
    # Check if the user is an admin
    # if not request.user.is_superuser:
    #     return HttpResponseForbidden("Access denied")

    notepad, created = Notepad.objects.get_or_create(machine=machine)

    if request.method == 'POST':
        form = NotepadForm(request.POST, instance=notepad)
        if form.is_valid():
            form.save()
            return redirect('machine_detail', machine_id=machine.id)
    else:
        form = NotepadForm(instance=notepad)

    return render(request, 'machines/edit_notepad.html', {'machine': machine, 'form': form})


class CustomLogoutView(LogoutView):
    def get_next_page(self):
        # Customize the redirection URL after logout here
        return reverse('login')
    template_name = 'machines/logout.html'


@login_required
def profile_view(request):
    return render(request, 'profile.html')


def send_booking_expiry_notification(user_name, user_email, machine_name):
    subject = 'Machine Booking Reminder'
    message = f'''Dear {user_name},\n\nYour booking for {machine_name} has ended. Please free the machine as soon as possible.
    \n\n ***This is an automated mail, don't reply.***'''
    from_email = 'kartikeymahajan321@gmail.com'  # Use the same email configured in settings.py
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)


def send_slack_message(name, vm_name):
    """ send message to our slack channel """
    
    payload = {"text": f"Hello {name}, Your booking for {vm_name} is expired. Please free up the machine"}
    response = requests.post(
       "https://hooks.slack.com/services/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",
        json=payload
    )
    print(response.text)

def send_slack_booking_notification(name, vm_name, end_time):

    """ send booking confirmation on slack """
    
    payload = {"text": f"{vm_name} is occupied by {name} till {end_time}"}
    response = requests.post(
       "https://hooks.slack.com/services/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",
       
        json=payload
    )
    print(response.text)

def send_slack_unbooking_notification(vm_name):

    """ send booking confirmation on slack """
    
    payload = {"text": f"{vm_name} is free now."}
    response = requests.post(
       "https://hooks.slack.com/services/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",
       
        json=payload
    )
    print(response.text)

def send_slack_hardware_details(data):
    
    """Send daily hardware updates on slack"""
    
    payload = {"text": data}
    response = requests.post(
       "https://hooks.slack.com/services/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",
       
        json=payload
    )
    print(response.text)
    

