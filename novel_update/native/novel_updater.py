import novel_scraper.models as models
import novel_scraper.native.cout_custom as cout
import enums_configs.native.novel_processor_cfg as np_cfg
import enums_configs.native.driver_manager_cfg as dm_cfg
import novel_processor.native.exceptions as np_exc
import novel_scraper.native.ns_exceptions as ns_exc
import novel_update.native.exceptions as nu_exc
import driver_manager.native.exceptions as dm_exc
import novel_processor.models as np_models
import driver_manager.models as dm_models
from enums_configs.native.enum_manager import EnumManager
from novel_scraper.native.scraping_manager import ScrapingManager
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
    def __init__(self, updater_func_type, source_site, driver=None) -> None:
        self.header = f"NOVEL_UPDATER::{updater_func_type}"
        self.loader = cout.COutLoading()

        self.source_site = source_site
        self.updater_func_type = updater_func_type
        self.updater_func = self.__get_updater_func()

        if np_models.NovelProcessPool.objects.count() > 1:
            raise nu_exc.MultipleNovelProcessPoolsExistException(self.header)
        elif np_models.NovelProcessPool.objects.count() == 0:
            raise nu_exc.NoProcessPoolExistsException(self.header)
        self.novel_process_pool = np_models.NovelProcessPool.objects.first()

        if dm_models.DriverPool.objects.count() > 1:
            raise nu_exc.DriverPoolsExistException(self.header)
        elif dm_models.DriverPool.objects.count() == 0:
            raise nu_exc.NoDriverPoolExistsException(self.header)
        self.driver_pool = dm_models.DriverPool.objects.first()

        if driver:
            self.driver = driver
        else:
            self.driver = self.__request_available_driver(self.driver_pool)

        cout.COut.broadcast(
            message="Initialization successful",
            header=self.header,
            style="success",
        )
        self.__update(
            np_cfg.PROCESS_PROGRESS_FAILURE_GRACE_PERIOD, self.updater_func, self.loader
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

    def __get_updater_func(self):
        if not NovelUpdaterType.is_updater_func_type_valid(self.updater_func_type):
            raise ns_exc.InvalidUpdaterFuncTypeException(self.updater_func_type)
        if self.updater_func_type == NovelUpdaterType.NOVEL_PROFILER:
            return NovelUpdater.__updater_novel_profiler
        elif self.updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_PROFILER:
            return NovelUpdater.__updater_novel_chapter_profiler
        elif self.updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_UPDATER:
            return NovelUpdater.__updater_novel_chapter_updater

    def __request_available_process(self):
        while True:
            try:
                process = self.novel_process_pool.get_available_process(
                    self.updater_func_type, self.source_site
                )
                return process
            except np_exc.ProcessPoolLockedException:
                cout.COut.broadcast(
                    f"Novel process pool is locked, awaiting for {np_cfg.POOL_REQUEST_ACCESS_DENIED_RETRY_PERIOD}s before retrying...",
                    header=self.header,
                    style="warning",
                )
            sleep(np_cfg.POOL_REQUEST_ACCESS_DENIED_RETRY_PERIOD)

    def __request_available_driver(self):
        while True:
            try:
                driver = self.driver_pool.get_available_driver()
                while not driver:
                    cout.COut.broadcast(
                        f"No available driver detected, awaiting for {dm_cfg.NO_AVAILABLE_DRIVER_RETRY_PERIOD}s before retrying..."
                    )
                    driver = self.driver_pool.get_available_driver()
                return driver
            except dm_exc.DriverPoolLockedException:
                cout.COut.broadcast(
                    f"Driver pool is locked, awaiting for {dm_cfg.POOL_REQUEST_ACCESS_DENIED_RETRY_PERIOD}s before retrying...",
                    header=self.header,
                    style="warning",
                )
            sleep(dm_cfg.POOL_REQUEST_ACCESS_DENIED_RETRY_PERIOD)

    def __update(self, progress_failure_grace_period, updater_func, loader):
        processes_updated = 0
        while True:
            GRACE_PERIOD_CURRENT = 0
            process = self.__request_available_process()
            if not process:
                break

            cout.COut.broadcast(
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
                except ns_exc.ScraperProcessFailureException as ex:
                    GRACE_PERIOD_CURRENT += 1
                    if GRACE_PERIOD_CURRENT >= progress_failure_grace_period:
                        process.release_process(self.updater_func_type)
                        raise nu_exc.NovelProcessFailureException(ex, process)
                    cout.COut.broadcast(
                        message=cout.Broadcasts.NOVEL_PROCESS_FAILURE_RETRY_BROADCAST.format(
                            current_grace_period=GRACE_PERIOD_CURRENT,
                            max_grace_period=progress_failure_grace_period,
                        ),
                        style="warning",
                        header=self.header + ex.header,
                    )
                except Exception as ex:
                    process.release_process(self.updater_func_type)
                    raise ex

            process.release_process(self.updater_func_type)
            processes_updated += 1

        cout.COut.broadcast(
            f"Couldn't find anymore available and/or update applicable processes. {processes_updated} processes updated.",
            header=self.header,
            style="success",
        )

        if self.updater_func_type == NovelUpdaterType.NOVEL_PROFILER:
            return NovelUpdater(
                NovelUpdaterType.NOVEL_CHAPTER_PROFILER,
                self.source_site,
                self.driver,
            )
        elif self.updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_PROFILER:
            return NovelUpdater(
                NovelUpdaterType.NOVEL_CHAPTER_UPDATER,
                self.source_site,
                self.driver,
            )
        else:
            return self.driver.release_driver()
