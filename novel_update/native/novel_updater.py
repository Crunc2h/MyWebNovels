import novel_scraper.models as models
import novel_scraper.native.novel_ppool_cfg as npcfg
import novel_scraper.native.ns_exceptions as nsexc
from novel_scraper.native.enum_manager import EnumManager
from novel_scraper.native.scraping_manager import ScrapingManager
from novel_scraper.native.cout_custom import COut, COutLoading
from novel_scraper.native.novel_ppool_cfg import POOL_REQUEST_ACCESS_DENIED_RETRY_PERIOD
from time import sleep


class NovelUpdaterType:
    NOVEL_PROFILER = "NOVEL_PROFILER"
    NOVEL_CHAPTER_PROFILER = "NOVEL_CHAPTER_PROFILER"
    NOVEL_CHAPTER_UPDATER = "NOVEL_CHAPTER_UPDATER"

    @staticmethod
    def is_updater_func_type_valid(updater_func_type):
        if updater_func_type == NovelUpdaterType.NOVEL_PROFILER:
            return True
        elif updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_PROFILER:
            return True
        elif updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_UPDATER:
            return True
        return False


class NovelUpdater:
    def __init__(
        self, updater_func_type, source_site, driver_pool, driver=None
    ) -> None:
        self.source_site = source_site
        self.updater_func_type = updater_func_type
        self.updater_func = NovelUpdater.__get_updater_func(updater_func_type)
        self.header = f"NOVEL_UPDATER::{updater_func_type}"
        self.loader = COutLoading()
        self.novel_process_pool = models.NovelProcessPool.objects.first()
        if not self.novel_process_pool:
            raise nsexc.NoProcessPoolExistsException(self.header)
        self.driver_pool = driver_pool
        if driver:
            self.driver = driver
        else:
            self.driver = self.__request_available_driver(self.driver_pool)
        COut.broadcast(
            message="Initialization successful",
            header=self.header,
            style="success",
        )
        self.__update(
            npcfg.PROCESS_PROGRESS_FAILURE_GRACE_PERIOD, self.updater_func, self.loader
        )

    @staticmethod
    def __updater_novel_profiler(
        process, scraper, progress_failure_grace_period, loader
    ):
        temp_novel_profile = scraper.get_novel_profile(
            progress_failure_grace_period, process.base_link, loader
        )
        if not process.novel_profile:
            novel_profile_obj = models.NovelProfile(
                name=temp_novel_profile["name"],
                author_name=EnumManager.get_or_create_enum_of_type(
                    temp_novel_profile["author_name"], models.Author
                ),
                number_of_chapters=temp_novel_profile["number_of_chapters"],
                completion_status=EnumManager.get_or_create_enum_of_type(
                    temp_novel_profile["completion_status"],
                    models.NovelCompletionStatus,
                ),
                summary=temp_novel_profile["summary"],
            )
            novel_profile_obj.save()
            [
                novel_profile_obj.categories.add(
                    EnumManager.get_or_create_enum_of_type(
                        category, models.NovelCategory
                    )
                )
                for category in temp_novel_profile["categories"]
            ]
            [
                novel_profile_obj.tags.add(
                    EnumManager.get_or_create_enum_of_type(tag, models.NovelTag)
                )
                for tag in temp_novel_profile["tags"]
            ]
            process.novel_profile = novel_profile_obj
            return
        process.novel_profile.number_of_chapters = temp_novel_profile[
            "number_of_chapters"
        ]
        process.novel_profile.completion_status = (
            EnumManager.get_or_create_enum_of_type(
                temp_novel_profile["completion_status"], models.NovelCompletionStatus
            )
        )
        process.novel_profile.summary = temp_novel_profile["summary"]

    @staticmethod
    def __updater_novel_chapter_profiler(
        process, scraper, progress_failure_grace_period, loader
    ):
        if not process.novel_profile:
            return
        temp_chapter_profiles = scraper.get_novel_chapter_profiles(
            progress_failure_grace_period, process.base_link, loader
        )
        if len(temp_chapter_profiles) == process.novel_profile.chapter_profiles.count():
            return
        profiled_chapters = [
            profiled_chapter.name
            for profiled_chapter in process.novel_profile.chapter_profiles.all()
        ]
        new_chapters = [
            models.ChapterProfile(
                novel_profile=process.novel_profile,
                link=chapter["link"],
                name=chapter["name"],
                number=chapter["number"],
                source_update_time=chapter["source_update_time"],
            )
            for chapter in temp_chapter_profiles
            if chapter["name"] not in profiled_chapters
        ]
        for chapter in new_chapters:
            chapter.save()

    @staticmethod
    def __updater_novel_chapter_updater(
        process, scraper, progress_failure_grace_period, loader
    ):
        if not process.novel_profile:
            return
        if process.novel_profile.chapter_profiles.count() == 0:
            return
        for chapter_profile in process.novel_profile.chapter_profiles.filter(
            already_exists=False
        ):
            temp_chapter_text = scraper.get_novel_chapter(
                progress_failure_grace_period, chapter_profile, loader
            )
            chapter_text_obj = models.ChapterText(
                chapter_profile=chapter_profile, text=temp_chapter_text
            )
            chapter_text_obj.save()

    @staticmethod
    def __get_updater_func(updater_func_type):
        if not NovelUpdaterType.is_updater_func_type_valid(updater_func_type):
            raise nsexc.InvalidUpdaterFuncTypeException(updater_func_type)
        if updater_func_type == NovelUpdaterType.NOVEL_PROFILER:
            return NovelUpdater.__updater_novel_profiler
        elif updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_PROFILER:
            return NovelUpdater.__updater_novel_chapter_profiler
        elif updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_UPDATER:
            return NovelUpdater.__updater_novel_chapter_updater

    def __request_available_process(self):
        while True:
            try:
                process = self.novel_process_pool.get_available_process(
                    self.updater_func_type, self.source_site
                )
                return process
            except nsexc.ProcessPoolLockedException:
                COut.broadcast(
                    f"Process pool is locked, awaiting for {POOL_REQUEST_ACCESS_DENIED_RETRY_PERIOD}s before retrying...",
                    header=self.header,
                    style="warning",
                )
                sleep(POOL_REQUEST_ACCESS_DENIED_RETRY_PERIOD)

    def __request_available_driver(self):
        while True:
            try:
                driver = self.driver_pool.get_available_driver()
                while not driver:
                    COut.broadcast(
                        f"Awaiting for an available driver...",
                        header=self.header,
                        style="warning",
                    )
                    sleep(POOL_REQUEST_ACCESS_DENIED_RETRY_PERIOD)
                    driver = self.driver_pool.get_available_driver()
                return driver
            except nsexc.DriverPoolLockedException:
                COut.broadcast(
                    f"Driver pool is locked, awaiting for {POOL_REQUEST_ACCESS_DENIED_RETRY_PERIOD}s before retrying...",
                    header=self.header,
                    style="warning",
                )
                sleep(POOL_REQUEST_ACCESS_DENIED_RETRY_PERIOD)

    def __update(self, progress_failure_grace_period, updater_func, loader):
        processes_updated = 0
        while True:
            GRACE_PERIOD_CURRENT = 0
            process = self.__request_available_process()
            if not process:
                break

            COut.broadcast(
                f"Beginning update on process {process.base_link}...",
                header=self.header,
                style="init",
            )

            scraper = ScrapingManager(process.source_site)
            while True:
                try:
                    updater_func(
                        process, scraper, progress_failure_grace_period, loader
                    )
                    break
                except nsexc.ScraperProcessFailureException as ex:
                    GRACE_PERIOD_CURRENT += 1
                    if GRACE_PERIOD_CURRENT >= progress_failure_grace_period:
                        process.release_process(self.updater_func_type)
                        raise nsexc.NovelProcessFailureException(ex, process)
                    COut.broadcast(
                        message=nsexc.NOVEL_PROCESS_FAILURE_RETRY_BROADCAST.format(
                            current_grace_period=GRACE_PERIOD_CURRENT
                        ),
                        style="warning",
                        header="NOVEL_UPDATER::" + ex.header,
                    )
                except Exception as ex:
                    process.release_process(self.updater_func_type)
                    raise ex

            process.release_process(self.updater_func_type)
            processes_updated += 1

        COut.broadcast(
            f"Couldn't find anymore available and/or update applicable processes. {processes_updated} processes updated.",
            header=self.header,
            style="success",
        )

        if self.updater_func_type == NovelUpdaterType.NOVEL_PROFILER:
            return NovelUpdater(
                NovelUpdaterType.NOVEL_CHAPTER_PROFILER,
                self.source_site,
                self.driver_pool,
                self.driver,
            )
        elif self.updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_PROFILER:
            return NovelUpdater(
                NovelUpdaterType.NOVEL_CHAPTER_UPDATER,
                self.source_site,
                self.driver_pool,
                self.driver,
            )
