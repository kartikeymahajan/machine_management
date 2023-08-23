from django.shortcuts import render, redirect
from .models import Machine, Booking
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .forms import BookingForm  # Import the BookingForm from forms.py
from django.shortcuts import redirect, get_object_or_404
from django. contrib import messages
from django.urls import reverse


@login_required
def machine_list(request):
    machines = Machine.objects.all()
    return render(request, 'machines/machine_list.html', {'machines': machines})

@login_required
def machine_detail(request, machine_id):
    # machine = Machine.objects.get(pk=machine_id)
    # return render(request, 'machines/machine_detail.html', {'machine': machine})
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
    # user_can_free = False  # Initialize a variable to check if the user can free the machine
    
    # if request.user.is_authenticated:
    #     # Check if there's an active booking by the user for this machine
    #     user_booking = Booking.objects.filter(machine=machine, user=request.user, end_time__gte=timezone.now()).first()
    #     if user_booking:
    #         user_can_free = True
    # else: 
    #     messages.info(request, "You need to log in to free this machine.")
    
    # print(f"user_can_free: {user_can_free}")  # Add this line for debugging
    # context = {
    #     'machine': machine,
    #     'user_can_free': user_can_free,  # Pass the variable to the template
    # }
    
    # return render(request, 'machines/machine_detail.html', context)

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
    
    # return redirect('machine_list')
    # return redirect(reverse('unbook_machine', args=[machine.id]))
    return render(request, 'unbook_machine.html', {'machine': machine, 'booking_form': unbook_machine})

    # machine = get_object_or_404(Machine, pk=machine_id)
    
    # # Check if there's an active booking for this machine
    # booking = machine.booking_set.filter(end_time__gte=timezone.now()).first()
    
    # if booking:
    #     if request.user == booking.user or request.user.is_superuser:
    #         # Delete the booking and update the machine status
    #         booking.delete()
    #         machine.status = True
    #         machine.save()
    #         messages.success(request, "You have successfully unbooked the machine.")
    #     else:
    #         messages.error(request, "You do not have permission to unbook this machine.")
    # else:
    #     messages.error(request, "No booking found to unbook.")
    
    # return redirect(reverse('machine_detail', args=[machine.id]))

