import time
from django.shortcuts import render, redirect
from .models import Machine, Booking, Notepad
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import BookingForm, NotepadForm 
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404, HttpResponseForbidden
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
            print(machine.name, request.user, machine.start_time.strftime("%m/%d/%Y, %H:%M:%S"), machine.end_time.strftime("%m/%d/%Y, %H:%M:%S"))
            print(Booking.end_time)
            date_time = machine.end_time.strftime("%m/%d/%Y, %H:%M:%S")
            print(f"ate_time{date_time}")
            send_slack_booking_notification(request.user, machine.name, date_time)

            return redirect('machine_list')
    
    return render(request, 'machines/book_machine.html', {'machine': machine, 'booking_form': booking_form})


@login_required
def extend_booking(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id, user=request.user, status=False)
    booking = Booking.objects.filter(machine=machine, user=request.user).first()

    if not booking:
        raise Http404("No active booking found for this machine.")

    if request.method == 'POST':
        booking_form = BookingForm(request.POST)
        if booking_form.is_valid():
            extend_duration = calculate_extend_duration(booking_form.cleaned_data)
            if machine.end_time <= timezone.now():
                machine.end_time = timezone.now()
                machine.nz_end_time = timezone.now()
                booking.end_time = timezone.now()
            machine.end_time += timedelta(minutes=extend_duration)
            machine.nz_end_time += timedelta(minutes=extend_duration)
            booking.end_time += timedelta(minutes=extend_duration)
            booking.notification_sent = False
            machine.save()
            booking.save()
            date_time = booking.end_time.strftime("%m/%d/%Y, %H:%M:%S")
            send_slack_booking_extend_notification(machine.name, date_time)
            # messages.success(request, 'Booking extended successfully.')
            return redirect('machine_list')

    else:
        booking_form = BookingForm()

    return render(
        request,
        'machines/extend_booking.html',
        {'machine': machine, 'booking': booking, 'booking_form': booking_form}
    )

def calculate_extend_duration(cleaned_data):
    days = cleaned_data.get('days', 0) if type(cleaned_data.get('days', 0))==int else 0
    hours = cleaned_data.get('hours', 0) if type(cleaned_data.get('hours', 0))==int else 0
    minutes = cleaned_data.get('minutes', 0) if type(cleaned_data.get('minutes', 0))==int else 0

    # Convert all durations to minutes and sum them up
    total_minutes = days * 24 * 60 + hours * 60 + minutes
    return total_minutes


@login_required
def unbook_machine(request, machine_id):
    machine = Machine.objects.get(pk=machine_id)
    # Check if the user has the authority to unbook this machine
    if machine.user == request.user:
        machine.status = True
        machine.user = None

        # deleting the record of VM from booking
        booking = Booking.objects.filter(machine__name=machine.name)
        booking.delete()
        machine.save()
        send_slack_unbooking_notification(machine.name)

        messages.success(request, "You have successfully unbooked the machine.")
    else:
        messages.error(request, "You do not have permission to unbook this machine.")

    return render(request, 'unbook_machine.html', {'machine': machine, 'booking_form': unbook_machine})

def auto_unbook_machine(machine_name):
    machine = Machine.objects.get(name = machine_name)
    machine.status = True
    machine.user = None
    # deleting the record of VM from booking
    booking = Booking.objects.filter(machine__name=machine.name)
    booking.delete()
    machine.save()
    send_slack_unbooking_notification(machine.name)

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

@login_required
def admin_redirect(request):
    return redirect('admin:index')


def send_booking_expiry_notification(user_name, user_email, machine_name):
    """Send booking expiry notification of users mail id"""

    machine_name = machine_name.replace('(ETH)', '').replace('(IB)', '')
    subject = 'Machine Unbook Reminder'
    message = f'''Dear {user_name},\n\nYour booking for {machine_name} has been ended.\n
    Please free up the machine or extend the booking period.\n

    Please make a note it will automatically free up in one hour.\n

    Thanks!\n

    \n\n **********This is an automated mail, don't reply.**********'''
    from_email = ''  # Use the same email configured in settings.py
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)


def send_slack_message(user_name, machine_name):
    """ send message to our slack channel """
    
    machine_name = machine_name.replace('(ETH)', '').replace('(IB)', '')
    payload = {"text": f"Hello {user_name}, Your booking for {machine_name} is expired. Please free up the machine"}
    response = requests.post(
       "https://hooks.slack.com/services/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",
        json=payload
    )
    print(response.text)

def send_slack_booking_notification(user_name, machine_name, end_time):

    """ send booking confirmation on slack """
    
    machine_name = machine_name.replace('(ETH)', '').replace('(IB)', '')
    payload = {"text": f"{machine_name} is occupied by {user_name} till {end_time}"}
    response = requests.post(
       "https://hooks.slack.com/services/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",
       
        json=payload
    )
    print(response.text)

def send_slack_booking_extend_notification(machine_name, end_time):

    """ send extend booking confirmation on slack """
    
    machine_name = machine_name.replace('(ETH)', '').replace('(IB)', '')
    payload = {"text": f"{machine_name} booking is extended till {end_time}"}
    response = requests.post(
       "https://hooks.slack.com/services/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",
       
        json=payload
    )
    print(response.text)

def send_slack_unbooking_notification(machine_name):

    """ send booking confirmation on slack """
    
    machine_name = machine_name.replace('(ETH)', '').replace('(IB)', '')
    payload = {"text": f"{machine_name} is free now."}
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

def send_booking_expiry_notification_on_slack(user_name, machine_name):
    """send booking expiry intimetion/warning on slack"""
    machine_name = machine_name.replace('(ETH)', '').replace('(IB)', '')
    payload = {"text": f"Hi {user_name}, Your booking for {machine_name} is over. Please free up the system or exeted it, if needed."}
    response = requests.post(
       "https://hooks.slack.com/services/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",
       
        json=payload
    )
    print(response.text)