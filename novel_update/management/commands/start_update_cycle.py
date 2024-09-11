from django.core.management.base import BaseCommand
from novel_update.native.novel_update_cycle import NovelUpdateCycle


class Command(BaseCommand):
    help = "Start a new novel update cycle"

    def add_arguments(self, parser):
        parser.add_argument("max_cc_ops_per_site", nargs="+", type=int)

    def handle(self, *args, **options):
        NovelUpdateCycle(options["max_cc_ops_per_site"][0])
