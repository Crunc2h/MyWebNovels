from novel_scraper.native.novel_updater import NovelUpdater, NovelUpdaterType
from novel_scraper.native.cout_custom import COut
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Spawns a new novel profiler to get relevant info"

    def add_arguments(self, parser):
        parser.add_argument("website", nargs="+", type=str)

    def handle(self, *args, **options):
            self.stdout.write(
                COut.get_styled("Spawning new novel profiler...", style="init", header="ADMIN")
            )
            NovelUpdater(NovelUpdaterType.NOVEL_PROFILER, options["website"][0])