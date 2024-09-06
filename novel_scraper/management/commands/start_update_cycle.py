from django.core.management.base import BaseCommand, CommandError
from novel_scraper.models import NovelUpdaterType, NovelUpdater

class Command(BaseCommand):
    help = "Closes the specified poll for voting"
    """
    def add_arguments(self, parser):
        parser.add_argument("poll_ids", nargs="+", type=int)"""

    def handle(self, *args, **options):
            NovelUpdater(NovelUpdaterType.NOVEL_PROFILER)
            self.stdout.write(
                self.style.SUCCESS('testing')
            )