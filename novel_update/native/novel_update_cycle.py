import os
import novel_scraper.models as models
import enums_configs.native.novel_ppool_cfg as npcfg
import novel_scraper.native.ns_exceptions as ns_exc
from driver_manager.native.driver_pool import DriverPool
from enums_configs.native.source_site import SourceSite
from novel_scraper.native.scraping_manager import ScrapingManager
from novel_scraper.native.cout_custom import COut, COutLoading
from datetime import datetime, timezone
from time import sleep


class NovelUpdateCycle:
    def __init__(self, max_concurrent_ops_per_site) -> None:
        self.header = "DB_UPDATE_CYCLE"
        self.loader = COutLoading()
        self.t_start = datetime.now(timezone.utc)
        self.sites = SourceSite.all()

        if models.NovelProcessPool.objects.count() > 1:
            raise ns_exc.MultipleProcessPoolsExistException(self.header)
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

        self.driver_pool = DriverPool(len(self.sites) * max_concurrent_ops_per_site)

        COut.broadcast("Initialization successful", style="success", header=self.header)

        """
        sites_and_links = []
        for site in self.sites:
            scraper = ScrapingManager(site)
            sites_and_links.append(
                (
                    scraper.get_all_novel_links(
                        npcfg.PROCESS_PROGRESS_FAILURE_GRACE_PERIOD, loader=self.loader
                    ),
                    site,
                )
            )

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

        for novel_links, site in sites_and_links:
            for link in novel_links:
                self.pool.initialize_process(link, site)

        for site in self.sites:
            for i in range(0, max_concurrent_ops_per_site):
                NovelUpdateCycle.spawn_novel_profiler(site)
                COut.broadcast(
                    f"Spawned a new profiler for {site}",
                    style="success",
                    header=self.header,
                )

        while self.pool.processes.filter(is_being_processed=True).count() > 0:
            COut.broadcast(
                "Update in progress...",
                header=self.header,
                style="progress",
                loader=self.loader,
            )
            sleep(0.5)

    @staticmethod
    def spawn_novel_profiler(source_site):
        command = (
            "gnome-terminal -- "
            + f"bash -c 'python3 manage.py spawn_novel_profiler '{source_site}'; exec bash'"
        )
        os.system(command)
