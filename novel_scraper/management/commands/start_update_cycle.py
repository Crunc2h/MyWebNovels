from novel_scraper.native.cout_custom import COut
from novel_scraper.native.novel_update_cycle import NovelUpdateCycle
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Starts the db update cycle"
    
    def add_arguments(self, parser):
        parser.add_argument("max_cc_ops_per_site", nargs="+", type=int)

    def handle(self, *args, **options):
            COut.broadcast("Beginning update...", style="init", header="ADMIN")

            NovelUpdateCycle(int(options["max_cc_ops_per_site"][0]))
