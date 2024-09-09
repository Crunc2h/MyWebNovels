from novel_scraper.native.enum_manager import EnumManager
from novel_scraper.native.novel_ppool_cfg import POOL_REQUEST_ACCESS_DENIED_RETRY_PERIOD
from novel_scraper.models import *


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
    def __init__(self, updater_func_type, source_site) -> None:
        self.pool = NovelProcessPool.objects.first()
        if not self.pool:
            raise Exception(f" [~NOVEL_UPDATER] > No process pool exists!")

        self.source_site = source_site
        self.updater_func_type = updater_func_type
        print(
            f" [~NOVEL_UPDATER::{updater_func_type}] > Initialized, beginning to update existing processes..."
        )
        self.__update(NovelUpdater.__get_updater_func(updater_func_type))

    @staticmethod
    def __updater_novel_profiler(process, scraper):
        temp_novel_profile = scraper.get_novel_profile(process.base_link)
        if not process.novel_profile:
            novel_profile_obj = NovelProfile(
                name=temp_novel_profile["name"],
                author_name=EnumManager.get_or_create_enum_of_type(
                    temp_novel_profile["author_name"], Author
                ),
                number_of_chapters=temp_novel_profile["number_of_chapters"],
                completion_status=EnumManager.get_or_create_enum_of_type(
                    temp_novel_profile["completion_status"], NovelCompletionStatus
                ),
                summary=temp_novel_profile["summary"],
            )
            novel_profile_obj.save()
            [
                novel_profile_obj.categories.add(
                    EnumManager.get_or_create_enum_of_type(category, NovelCategory)
                )
                for category in temp_novel_profile["categories"]
            ]
            [
                novel_profile_obj.tags.add(
                    EnumManager.get_or_create_enum_of_type(tag, NovelTag)
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
                temp_novel_profile["completion_status"], NovelCompletionStatus
            )
        )
        process.novel_profile.summary = temp_novel_profile["summary"]

    @staticmethod
    def __updater_novel_chapter_profiler(process, scraper):
        if not process.novel_profile:
            return
        temp_chapter_profiles = scraper.get_novel_chapter_profiles(process.base_link)
        if len(temp_chapter_profiles) == process.novel_profile.chapter_profiles.count():
            return
        profiled_chapters = [
            profiled_chapter.name
            for profiled_chapter in process.novel_profile.chapter_profiles.all()
        ]
        new_chapters = [
            ChapterProfile(
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
    def __updater_novel_chapter_updater(process, scraper):
        if not process.novel_profile:
            return
        if process.novel_profile.chapter_profiles.count() == 0:
            return
        for chapter_profile in process.novel_profile.chapter_profiles.filter(
            already_exists=False
        ):
            temp_chapter_text = scraper.get_novel_chapter(chapter_profile)
            chapter_text_obj = ChapterText(
                chapter_profile=chapter_profile, text=temp_chapter_text
            )
            chapter_text_obj.save()

    @staticmethod
    def __get_updater_func(updater_func_type):
        if not NovelUpdaterType.is_updater_func_type_valid(updater_func_type):
            raise Exception(
                f" [~NOVEL_UPDATER] > {updater_func_type} is an invalid updater function type"
            )
        if updater_func_type == NovelUpdaterType.NOVEL_PROFILER:
            return NovelUpdater.__updater_novel_profiler
        elif updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_PROFILER:
            return NovelUpdater.__updater_novel_chapter_profiler
        elif updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_UPDATER:
            return NovelUpdater.__updater_novel_chapter_updater

    def __request_available_process(self):
        while True:
            try:
                process = self.pool.get_available_process(
                    self.updater_func_type, self.source_site
                )
                return process
            except PermissionDenied:
                sleep(POOL_REQUEST_ACCESS_DENIED_RETRY_PERIOD)

    def __update(self, updater_func):
        processes_updated = 0
        while True:
            process = self.__request_available_process()
            if not process:
                break
            print(
                f" [~NOVEL_UPDATER::{self.updater_func_type}] > Beginning update on process {process.base_link}..."
            )
            scraper = ScrapingManager(process.source_site)
            updater_func(process, scraper)
            process.release_process(self.updater_func_type)
            processes_updated += 1
        print(
            f" [~NOVEL_UPDATER::{self.updater_func_type}] > Couldn't find anymore available and/or update applicable processes. {processes_updated} processes updated."
        )
        if self.updater_func_type == NovelUpdaterType.NOVEL_PROFILER:
            return NovelUpdater(
                NovelUpdaterType.NOVEL_CHAPTER_PROFILER, self.source_site
            )
        elif self.updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_PROFILER:
            return NovelUpdater(
                NovelUpdaterType.NOVEL_CHAPTER_UPDATER, self.source_site
            )
