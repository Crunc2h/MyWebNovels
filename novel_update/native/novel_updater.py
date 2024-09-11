import novel_scraper.models as models
import novel_scraper.native.cout_custom as cout
import enums_configs.native.novel_processor_cfg as np_cfg
import novel_processor.native.exceptions.novel_processor_exceptions as np_exc
import novel_scraper.native.ns_exceptions as Broadcasts
import novel_update.native.exceptions.novel_update_exceptions as nu_exc
import novel_processor.models as np_models
import enums_configs.native.novel_update_cfg as nu_cfg
import novel_storage.models as nst_models
from enums_configs.native.enum_manager import EnumManager
from novel_scraper.native.scraping_manager import ScrapingManager
from time import sleep


class NovelUpdaterType:
    ALL_NOVEL_LINKS = "ALL_NOVEL_LINKS"
    NOVEL_PROFILER = "NOVEL_PROFILER"
    NOVEL_CHAPTER_PROFILER = "NOVEL_CHAPTER_PROFILER"
    NOVEL_CHAPTER_UPDATER = "NOVEL_CHAPTER_UPDATER"

    @staticmethod
    def is_updater_func_type_valid(updater_func_type):
        if (
            updater_func_type == NovelUpdaterType.ALL_NOVEL_LINKS
            or updater_func_type == NovelUpdaterType.NOVEL_PROFILER
            or updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_PROFILER
            or updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_UPDATER
        ):
            return True
        return False


class NovelUpdater:
    def __init__(self, updater_func_type, source_site) -> None:
        self.header = f"NOVEL_UPDATER::{updater_func_type}"
        self.loader = cout.COutLoading()

        self.source_site = source_site
        self.updater_func_type = updater_func_type
        self.updater_func = self.__get_updater_func()

        self.process_failure_grace_period = nu_cfg.PROCESS_FAILURE_GRACE_PERIOD

        if np_models.NovelProcessPool.objects.count() > 1:
            raise nu_exc.MultipleNovelProcessPoolsExistException(self.header)
        elif np_models.NovelProcessPool.objects.count() == 0:
            raise nu_exc.NoNovelProcessPoolExistsException(self.header)
        self.novel_process_pool = np_models.NovelProcessPool.objects.first()

        cout.COut.broadcast(
            message="Initialization successful",
            header=self.header,
            style="success",
        )

        if self.updater_func_type != NovelUpdaterType.ALL_NOVEL_LINKS:
            self.__update()
        else:
            self.updater_func()

    def __updater_all_novel_links(self):
        while True:
            GRACE_PERIOD_CURRENT = 0
            scraper = ScrapingManager(self.source_site)

            try:
                links = scraper.get_all_novel_links(self.loader)
                for link in links:
                    t_link = nst_models.TempNovelLink(
                        link=link, source_site=self.source_site
                    )
                    t_link.save()
                return
            except Broadcasts.ScraperProgressFailureException as ex:
                GRACE_PERIOD_CURRENT += 1
                if GRACE_PERIOD_CURRENT >= self.progress_failure_grace_period:
                    raise nu_exc.NovelLinksCollectorFailureException(ex)
                cout.COut.broadcast(
                    message=cout.Broadcasts.NOVEL_LINKS_COLLECTOR_FAILURE_RETRY_BROADCAST.format(
                        current_grace_period=GRACE_PERIOD_CURRENT,
                        max_grace_period=self.progress_failure_grace_period,
                    ),
                    style="warning",
                    header=self.header + "::" + ex.header,
                )

    def __updater_novel_profiler(self, process, scraper):
        temp_novel_profile = scraper.get_novel_profile(
            self.process_failure_grace_period,
            process.base_link,
            self.loader,
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

    def __updater_novel_chapter_profiler(self, process, scraper):
        if not process.novel_profile:
            return
        temp_chapter_profiles = scraper.get_novel_chapter_profiles(
            self.progress_failure_grace_period,
            process.base_link,
            self.loader,
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

    def __updater_novel_chapter_updater(self, process, scraper):
        if not process.novel_profile:
            return
        if process.novel_profile.chapter_profiles.count() == 0:
            return
        for chapter_profile in process.novel_profile.chapter_profiles.filter(
            already_exists=False
        ):
            temp_chapter_text = scraper.get_novel_chapter(
                self.progress_failure_grace_period,
                chapter_profile,
                self.loader,
            )
            chapter_text_obj = models.ChapterText(
                chapter_profile=chapter_profile, text=temp_chapter_text
            )
            chapter_text_obj.save()

    def __get_updater_func(self):
        if not NovelUpdaterType.is_updater_func_type_valid(self.updater_func_type):
            raise Broadcasts.InvalidUpdaterFuncTypeException(self.updater_func_type)
        if self.updater_func_type == NovelUpdaterType.ALL_NOVEL_LINKS:
            return self.__updater_all_novel_links
        elif self.updater_func_type == NovelUpdaterType.NOVEL_PROFILER:
            return self.__updater_novel_profiler
        elif self.updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_PROFILER:
            return self.__updater_novel_chapter_profiler
        return self.__updater_novel_chapter_updater

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

    def __update(self):
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
                    self.updater_func(process, scraper, self.loader)
                    GRACE_PERIOD_CURRENT = 0
                    break
                except Broadcasts.ScraperProgressFailureException as ex:
                    GRACE_PERIOD_CURRENT += 1
                    if GRACE_PERIOD_CURRENT >= self.progress_failure_grace_period:
                        process.release_process(self.updater_func_type)
                        raise nu_exc.NovelProcessFailureException(ex, process)
                    cout.COut.broadcast(
                        message=cout.Broadcasts.NOVEL_PROCESS_FAILURE_RETRY_BROADCAST.format(
                            current_grace_period=GRACE_PERIOD_CURRENT,
                            max_grace_period=self.progress_failure_grace_period,
                        ),
                        style="warning",
                        header=self.header + "::" + ex.header,
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
            )
        elif self.updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_PROFILER:
            return NovelUpdater(
                NovelUpdaterType.NOVEL_CHAPTER_UPDATER,
                self.source_site,
            )
