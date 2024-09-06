import os
from datetime import datetime, timezone, timedelta
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, PermissionDenied
from time import sleep
from django.utils.translation import gettext_lazy as _
from .native.webnovelpub import *


class Author(models.Model):
    name = models.CharField(max_length=512)
class NovelCategory(models.Model):
    name = models.CharField(max_length=512)

class NovelTag(models.Model):
    name = models.CharField(max_length=512)

class NovelCompletionStatus(models.Model):
    name = models.CharField(max_length=512)

class NovelLanguage(models.Model):
    name = models.CharField(max_length=512)

class EnumManager:
    @staticmethod
    def get_or_create_enum_of_type(enum_str, enum_type):
        enum_str = enum_str.lower()
        try:
            matching_enum = enum_type.objects.get(name=enum_str)
            return matching_enum
        except ObjectDoesNotExist:
            new_enum = enum_type(name=enum_str)
            new_enum.save()
            return new_enum
        except MultipleObjectsReturned:
            raise Exception(f" [~ENUM_MANAGER] > Multiple objects of type {enum_type} and str {enum_str} exists!")
        

class NovelSourceSite(models.TextChoices):
    WEBNOVELPUB = "webnovelpub.com", _("webnovelpub.com")

    def all(): return [
        NovelSourceSite.WEBNOVELPUB
    ]


class ScrapingManagerConfig:
    def get_config(source_site):
        if source_site == NovelSourceSite.WEBNOVELPUB:
            return {
                "scrape_all_novel_links": webnovelpub__scrape_all_novel_links,
                "scrape_novel_profile": webnovelpub__scrape_novel_profile,
                "scrape_novel_chapter_profiles": webnovelpub__scrape_novel_chapter_profiles,
                "scrape_novel_chapters": webnovelpub__scrape_novel_chapters
            }

class ScrapingManager:
    def __init__(self, source_site=NovelSourceSite.WEBNOVELPUB):
        config = ScrapingManagerConfig.get_config(source_site)
        self.sc_all_novel_links = config["scrape_all_novel_links"]
        self.sc_novel_profile = config["scrape_novel_profile"]
        self.sc_novel_chapter_profiles = config["scrape_novel_chapter_profiles"]
        self.sc_novel_chapters = config["scrape_novel_chapters"]
    
    def __scrape_all_novel_links(self): return self.sc_all_novel_links()
    def __scrape_novel_profile(self, novel_base_link): return self.sc_novel_profile(novel_base_link)   
    def __scrape_novel_chapter_profiles(self, novel_base_link): return self.sc_novel_chapter_profiles(novel_base_link)    
    def __scrape_novel_chapters(self, chapter_profile): return self.sc_novel_chapters(chapter_profile)
    
    def get_all_novel_links(self): return self.__scrape_all_novel_links()
    def get_novel_profile(self, novel_base_link): return self.__scrape_novel_profile(novel_base_link)
    def get_novel_chapter_profiles(self, novel_base_link): return self.__scrape_novel_chapter_profiles(novel_base_link)
    def get_novel_chapter(self, chapter_profile): return self.__scrape_novel_chapters(chapter_profile)


class NovelProfile(models.Model):    
    name = models.CharField(max_length=1024)
    language = models.ForeignKey(NovelLanguage, on_delete=models.PROTECT ,blank=True, null=True, related_name="profiles")
    completion_status = models.ForeignKey(NovelCompletionStatus, on_delete=models.PROTECT, related_name="profiles")
    author_name = models.ForeignKey(Author, on_delete=models.PROTECT, related_name="profiles")
    number_of_chapters = models.IntegerField()

    summary = models.TextField(max_length=16256)

    categories = models.ManyToManyField(NovelCategory, related_name="profiles")
    tags = models.ManyToManyField(NovelTag, related_name="profiles")

class ChapterProfile(models.Model):
    novel_profile = models.ForeignKey(NovelProfile, on_delete=models.CASCADE, related_name="chapter_profiles", blank=True, null=True)
    already_exists = models.BooleanField(default=False)
    name = models.CharField(max_length=1024)
    link = models.CharField(max_length=8128)
    number = models.CharField(max_length=64)
    source_update_time = models.CharField(max_length=512)

class ChapterText(models.Model):
    chapter_profile = models.OneToOneField(ChapterProfile, on_delete=models.CASCADE, related_name="chapter_text")
    text = models.TextField(max_length=65024)

PROCESS_CONTROL_THRESHOLD = 120

class NovelProcessPool(models.Model):
    locked = models.BooleanField(default=False)

    def initialize_process(self, process_base_link, process_source_site):
        self.locked = True
        if self.processes.filter(base_link=process_base_link).count() == 0:
            process = NovelProcess(pool=self, base_link=process_base_link, source_site=process_source_site)
            process.save()
        self.locked  = False
    
    def is_process(self, process_base_link):
        self.locked = True
        res = self.processes.filter(base_link=process_base_link).count() > 0
        self.locked = False
        return res

    def get_available_process(self, requesting_updater_func_type, requesting_updater_func_source_site):
        if self.locked: raise PermissionDenied()
        if not NovelUpdaterType.is_updater_func_type_valid(requesting_updater_func_type): raise Exception(f" [~NOVEL_PROCESS_POOL] > {requesting_updater_func_type} is an invalid requesting updater function type!")
        
        self.locked = True
        
        processes = self.processes.filter(is_being_processed=False, source_site=requesting_updater_func_source_site)
        if processes.count() == 0: 
            self.locked = False
            return None
        
        for process in processes:
            if requesting_updater_func_type ==  NovelUpdaterType.NOVEL_PROFILER: process_time = process.last_processed_by_novel_profiler
            elif requesting_updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_PROFILER: process_time = process.last_processed_by_novel_chapter_profiler
            elif requesting_updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_UPDATER: process_time = process.last_processed_by_novel_chapter_updater
            if (datetime.now(timezone.utc) - process_time).seconds // 60 >= PROCESS_CONTROL_THRESHOLD:
                process.activate_process()
                self.locked = False
                return process
        self.locked = False
        return None
    


class NovelProcess(models.Model):
    created = models.DateTimeField(auto_now=True)
    is_being_processed = models.BooleanField(default=False)
    last_processed_by_novel_profiler = models.DateTimeField(default=datetime.now(timezone.utc) - timedelta(minutes=PROCESS_CONTROL_THRESHOLD))
    last_processed_by_novel_chapter_profiler = models.DateTimeField(default=datetime.now(timezone.utc) - timedelta(minutes=PROCESS_CONTROL_THRESHOLD))
    last_processed_by_novel_chapter_updater = models.DateTimeField(default=datetime.now(timezone.utc) - timedelta(minutes=PROCESS_CONTROL_THRESHOLD))
    
    pool = models.ForeignKey(NovelProcessPool, on_delete=models.CASCADE, related_name="processes")
    
    source_site = models.CharField(max_length=256, choices=NovelSourceSite.choices)
    base_link = models.CharField(max_length=8128)

    novel_profile = models.OneToOneField(NovelProfile, on_delete=models.PROTECT, related_name="process", blank=True, null=True)

    def activate_process(self):
        if self.is_being_processed: raise Exception(f" [~NOVEL_PROCESS::{self.source_site}::{self.base_link}] > Trying to activate an already active process!")
        self.is_being_processed = True
        self.save()
    
    def release_process(self, releaser_updater_func_type):
        if not self.is_being_processed: raise Exception(f" [~NOVEL_PROCESS::{self.source_site}::{self.base_link}] > Trying to release an already inactive process!")
        if releaser_updater_func_type ==  NovelUpdaterType.NOVEL_PROFILER: self.last_processed_by_novel_profiler = datetime.now(timezone.utc)
        elif releaser_updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_PROFILER: self.last_processed_by_novel_chapter_profiler = datetime.now(timezone.utc)
        elif releaser_updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_UPDATER: self.last_processed_by_novel_chapter_updater = datetime.now(timezone.utc)
        self.is_being_processed = False
        self.save()
    

class NovelUpdaterType:
    NOVEL_PROFILER = "NOVEL_PROFILER"
    NOVEL_CHAPTER_PROFILER = "NOVEL_CHAPTER_PROFILER"
    NOVEL_CHAPTER_UPDATER = "NOVEL_CHAPTER_UPDATER"

    @staticmethod
    def is_updater_func_type_valid(updater_func_type):
        if updater_func_type == NovelUpdaterType.NOVEL_PROFILER: return True
        elif updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_PROFILER: return True
        elif updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_UPDATER: return True
        return False

POOL_REQUEST_ACCESS_DENIED_RETRY_PERIOD = 0.1
class NovelUpdater:
    def __init__(self, updater_func_type, source_site) -> None:
        self.pool = NovelProcessPool.objects.first()
        if not self.pool: raise Exception(f" [~NOVEL_UPDATER] > No process pool exists!")
        
        self.source_site = source_site
        self.updater_func_type = updater_func_type
        print(f" [~NOVEL_UPDATER::{updater_func_type}] > Initialized, beginning to update existing processes...")
        self.__update(NovelUpdater.__get_updater_func(updater_func_type))
    
    @staticmethod
    def __updater_novel_profiler(process, scraper):
        temp_novel_profile = scraper.get_novel_profile(process.base_link)
        if not process.novel_profile:
            novel_profile_obj = NovelProfile(name=temp_novel_profile["name"],
                                             author_name= EnumManager.get_or_create_enum_of_type(temp_novel_profile["author_name"], Author),
                                             number_of_chapters=temp_novel_profile["number_of_chapters"],
                                             completion_status=EnumManager.get_or_create_enum_of_type(temp_novel_profile["completion_status"], NovelCompletionStatus),
                                             summary=temp_novel_profile["summary"])
            novel_profile_obj.save()
            [novel_profile_obj.categories.add(EnumManager.get_or_create_enum_of_type(category, NovelCategory)) for category in temp_novel_profile["categories"]]
            [novel_profile_obj.tags.add(EnumManager.get_or_create_enum_of_type(tag, NovelTag)) for tag in temp_novel_profile["tags"]]
            process.novel_profile = novel_profile_obj
            return 
        process.novel_profile.number_of_chapters = temp_novel_profile["number_of_chapters"]
        process.novel_profile.completion_status = EnumManager.get_or_create_enum_of_type(temp_novel_profile["completion_status"], NovelCompletionStatus)
        process.novel_profile.summary = temp_novel_profile["summary"]
        
    @staticmethod
    def __updater_novel_chapter_profiler(process, scraper):
        if not process.novel_profile : return
        temp_chapter_profiles = scraper.get_novel_chapter_profiles(process.base_link)
        if len(temp_chapter_profiles) == process.novel_profile.chapter_profiles.count(): return
        profiled_chapters = [profiled_chapter.name for profiled_chapter in process.novel_profile.chapter_profiles.all()]
        new_chapters = [ChapterProfile(novel_profile=process.novel_profile,
                                       link=chapter["link"],
                                       name=chapter["name"],
                                       number=chapter["number"],
                                       source_update_time=chapter["source_update_time"]) for chapter in temp_chapter_profiles if chapter["name"] not in profiled_chapters]
        for chapter in new_chapters: chapter.save()

    @staticmethod
    def __updater_novel_chapter_updater(process, scraper):
        if not process.novel_profile: return
        if process.novel_profile.chapter_profiles.count() == 0: return
        for chapter_profile in process.novel_profile.chapter_profiles.filter(already_exists=False):
            temp_chapter_text = scraper.get_novel_chapter(chapter_profile)
            chapter_text_obj = ChapterText(chapter_profile=chapter_profile,
                                           text=temp_chapter_text)
            chapter_text_obj.save()
    
    @staticmethod
    def __get_updater_func(updater_func_type):
        if not NovelUpdaterType.is_updater_func_type_valid(updater_func_type): raise Exception(f" [~NOVEL_UPDATER] > {updater_func_type} is an invalid updater function type")
        if updater_func_type == NovelUpdaterType.NOVEL_PROFILER: return NovelUpdater.__updater_novel_profiler
        elif updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_PROFILER: return NovelUpdater.__updater_novel_chapter_profiler
        elif updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_UPDATER: return NovelUpdater.__updater_novel_chapter_updater

    def __request_available_process(self):
        while True:
            try:
                process = self.pool.get_available_process(self.updater_func_type, self.source_site)
                return process
            except PermissionDenied:
                sleep(POOL_REQUEST_ACCESS_DENIED_RETRY_PERIOD)

    
    def __update(self, updater_func):
        processes_updated = 0
        while True:
            process = self.__request_available_process()
            if not process:
                break
            print(f" [~NOVEL_UPDATER::{self.updater_func_type}] > Beginning update on process {process.base_link}...")
            scraper = ScrapingManager(process.source_site)
            updater_func(process, scraper)
            process.release_process(self.updater_func_type)
            processes_updated += 1
        print(f" [~NOVEL_UPDATER::{self.updater_func_type}] > Couldn't find anymore available and/or update applicable processes. {processes_updated} processes updated.")
        if self.updater_func_type == NovelUpdaterType.NOVEL_PROFILER: return NovelUpdater(NovelUpdaterType.NOVEL_CHAPTER_PROFILER, self.source_site)
        elif self.updater_func_type == NovelUpdaterType.NOVEL_CHAPTER_PROFILER: return NovelUpdater(NovelUpdaterType.NOVEL_CHAPTER_UPDATER, self.source_site)


def spawn_novel_profiler():
        os.system("gnome-terminal -e 'bash -c \"source .venv/bin/activate; python3 manage.py spawn_novel_profiler; read\"'")


 























        
