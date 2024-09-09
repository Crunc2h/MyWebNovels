import os
import novel_scraper.models as models
import novel_scraper.native.cout_custom as cout
import novel_scraper.native.ns_exceptions as nsexc
from novel_scraper.native.source_site import SourceSite
from novel_scraper.native.scraping_manager import ScrapingManager
from novel_scraper.native.cout_custom import COut
from datetime import datetime, timezone


class NovelUpdateCycle:
    def __init__(self, max_concurrent_ops_per_site) -> None:
        self.header = "DB_UPDATE_CYCLE"
        self.t_start = datetime.now(timezone.utc)
        self.sites = SourceSite.all()
        COut.broadcast("Beginning update...", style="init", header=self.header)

        if models.NovelProcessPool.objects.count() > 1:
            raise nsexc.MultipleProcessPoolsExistException(self.header)
        elif models.NovelProcessPool.objects.count() == 0:
            COut.broadcast(
                "No process pool detected, creating a new one...",
                style="warning",
                header=self.header,
            )
            self.pool = models.NovelProcessPool()
            self.pool.save()
            COut.broadcast(
                "New process pool is successfully created.",
                style="success",
                header=self.header,
            )
        else:
            self.pool = models.NovelProcessPool.objects.first()
        sites_and_links = []
        for site in self.sites:
            scraper = ScrapingManager(site)
            sites_and_links.append((scraper.get_all_novel_links(), site))

        """
        models.NovelProcess.objects.all().delete()
        sites_and_links = [
            (
                [
                    "https://www.webnovelpub.pro/novel/a-depressed-kendo-player-possesses-a-bastard-aristocrat",
                    "https://www.webnovelpub.pro/novel/the-31st-piece-turns-the-tables",
                    "https://www.webnovelpub.pro/novel/the-narrow-eyed-villain-of-the-demon-academy",
                ],
                "webnovelpub.com",
            )
        ]
        """

        for novel_links, site in sites_and_links:
            for link in novel_links:
                self.pool.initialize_process(link, site)

        for site in self.sites:
            for i in range(0, max_concurrent_ops_per_site):
                NovelUpdateCycle.spawn_novel_profiler(site)

    @staticmethod
    def spawn_novel_profiler(source_site):
        command = (
            "gnome-terminal -e "
            + '"'
            + f"bash -c 'python3 manage.py spawn_novel_profiler '{source_site}'; exec bash'"
            + '"'
        )
        os.system(command)
