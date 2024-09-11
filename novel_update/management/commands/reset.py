from django.core.management.base import BaseCommand
import enums_configs.models as ec_models
import novel_processor.models as np_models
import novel_storage.models as ns_models
import novel_scraper.native.cout_custom as cout


class Command(BaseCommand):
    help = "DBWideReset"

    def handle(self, *args, **options):
        cout.COut.broadcast("!!! FULL DB RESET !!!", style="fail", header="ADMIN")
        np_models.NovelProcessPool.objects.all().delete()
        np_models.NovelProcess.objects.all().delete()
        ns_models.NovelProfile.objects.all().delete()
        ns_models.ChapterProfile.objects.all().delete()
        ns_models.ChapterText.objects.all().delete()
        ns_models.TempNovelLink.objects.all().delete()
        ec_models.Author.objects.all().delete()
        ec_models.NovelCategory.objects.all().delete()
        ec_models.NovelTag.objects.all().delete()
        ec_models.NovelCompletionStatus.objects.all().delete()
        ec_models.NovelLanguage.objects.all().delete()
        ec_models.NovelSourceSite.objects.all().delete()
        temp_b = ec_models.NovelSourceSite(name="webnovelpub.com")
        temp_b.save()
        cout.COut.broadcast("DB successfully reset", style="success", header="ADMIN")
