from django.core.management.base import BaseCommand
from novel_update.native.novel_updater import NovelUpdater, NovelUpdaterType


class Command(BaseCommand):
    help = "Spawns a new novel profiler to get relevant info"

    def add_arguments(self, parser):
        parser.add_argument("website", nargs="+", type=str)

    def handle(self, *args, **options):
        NovelUpdater(NovelUpdaterType.NOVEL_PROFILER, options["website"][0])
