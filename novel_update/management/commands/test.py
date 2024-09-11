from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = "DBWideReset"

    def handle(self, *args, **options):
        command = f"bash -c 'python3 manage.py reset; python3 manage.py start_update_cycle 10;' exec bash"
        os.system(command)
