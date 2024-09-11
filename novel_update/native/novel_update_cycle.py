import os
import novel_scraper.native.cout_custom as cout
import novel_update.native.exceptions.novel_update_exceptions as nu_exc
from novel_processor.models import NovelProcessPool
from novel_storage.models import TempNovelLink
from enums_configs.models import NovelSourceSite
from datetime import datetime, timezone
from time import sleep


class NovelUpdateCycle:
    def __init__(self, max_concurrent_ops_per_site) -> None:
        self.header = "DB_UPDATE_CYCLE"
        self.loader = cout.COutLoading()
        self.t_start = datetime.now(timezone.utc)
        self.sites = NovelSourceSite.objects.all()

        if NovelProcessPool.objects.count() > 1:
            raise nu_exc.MultipleNovelProcessPoolsExistException(self.header)
        elif NovelProcessPool.objects.count() == 0:
            cout.COut.broadcast(
                "No process pool detected, creating a new one...",
                style="warning",
                header=self.header,
            )
            self.novel_process_pool = NovelProcessPool()
            self.novel_process_pool.save()
            cout.COut.broadcast(
                "New process pool is successfully created.",
                style="success",
                header=self.header,
            )
        else:
            self.novel_process_pool = NovelProcessPool.objects.first()

        if TempNovelLink.objects.count() > 0:
            cout.COut.broadcast(
                f"Deleting temporary novel links from previous cycle, {TempNovelLink.objects.count()} links present...",
                style="warning",
                header=self.header,
            )
            TempNovelLink.objects.all().delete()

        for site in self.sites:
            NovelUpdateCycle.spawn_novel_links_collector(site.name)
            cout.COut.broadcast(
                f"Spawned a new links collector for {site.name}",
                style="success",
                header=self.header,
            )

        while TempNovelLink.objects.count() == 0:
            cout.COut.broadcast(
                "Update in progress...",
                header=self.header,
                style="progress",
                loader=self.loader,
            )
            sleep(0.5)

        cout.COut.broadcast(
            "Initializing new processes...",
            header=self.header,
            style="progress",
            loader=self.loader,
        )
        sleep(5)
        for temp_link in TempNovelLink.objects.all():
            self.novel_process_pool.initialize_process(
                temp_link.link, temp_link.source_site
            )
        cout.COut.broadcast(
            "Initialized new processes form temporary links",
            header=self.header,
            style="success",
        )
        sleep(5)
        NovelUpdateCycle.update_report()
        for site in self.sites:
            for i in range(0, max_concurrent_ops_per_site):
                NovelUpdateCycle.spawn_novel_profiler(site.name)
                cout.COut.broadcast(
                    f"Spawned a new profiler for {site.name}",
                    style="success",
                    header=self.header,
                )

        while (
            self.novel_process_pool.processes.filter(is_being_processed=True).count()
            > 0
        ):
            cout.COut.broadcast(
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

    @staticmethod
    def spawn_novel_links_collector(source_site):
        command = (
            "gnome-terminal -- "
            + f"bash -c 'python3 manage.py spawn_novel_links_collector '{source_site}';'"
        )
        os.system(command)

    @staticmethod
    def update_report():
        command = (
            "gnome-terminal -- "
            + f"bash -c 'python3 manage.py update_report; exec bash'"
        )
        os.system(command)
