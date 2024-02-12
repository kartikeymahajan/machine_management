from django.core.management.base import BaseCommand
from machines.models import Machine
from machines.views import send_slack_hardware_details

class Command(BaseCommand):
    help = 'Send hardware details on daily basis'
    msg = 'Hardware Updates'
    def handle(self, *args, **kwargs):
        # Get all machines
        all_machines = Machine.objects.all()

        data = ""

        for machine in all_machines:
            if machine.status:
                data += f"{machine.name.replace('(ETH)', '').replace('(IB)', '')}: Free\n"
            else:
                data += f"{machine.name.replace('(ETH)', '').replace('(IB)', '')}: {machine.user} - ({machine.purpose})\n"
        
        send_slack_hardware_details(data)