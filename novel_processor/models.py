import enums_configs.native.novel_processor_cfg as npcfg
import novel_processor.native.exceptions.novel_processor_exceptions as npexc
from django.db import models
from datetime import datetime, timezone, timedelta


class NovelProcessPool(models.Model):
    locked = models.BooleanField(default=False)

    def initialize_process(self, process_base_link, process_source_site):
        self.locked = True
        if self.processes.filter(base_link=process_base_link).count() == 0:
            process = NovelProcess(
                pool=self,
                base_link=process_base_link,
                source_site=process_source_site,
                last_processed_by_novel_profiler=datetime.now(timezone.utc)
                - timedelta(minutes=npcfg.PROCESS_CONTROL_THRESHOLD + 5),
                last_processed_by_novel_chapter_profiler=datetime.now(timezone.utc)
                - timedelta(minutes=npcfg.PROCESS_CONTROL_THRESHOLD + 5),
                last_processed_by_novel_chapter_updater=datetime.now(timezone.utc)
                - timedelta(minutes=npcfg.PROCESS_CONTROL_THRESHOLD + 5),
            )
            process.save()
        self.locked = False

    def is_process(self, process_base_link):
        self.locked = True
        res = self.processes.filter(base_link=process_base_link).count() > 0
        self.locked = False
        return res

    def get_available_process(
        self, requesting_updater_func_type, requesting_updater_func_source_site
    ):
        if self.locked:
            raise npexc.ProcessPoolLockedException()
        if not novel_updater.NovelUpdaterType.is_updater_func_type_valid(
            requesting_updater_func_type
        ):
            raise npexc.InvalidUpdaterFuncTypeException(requesting_updater_func_type)

        self.locked = True

        processes = self.processes.filter(
            is_being_processed=False, source_site=requesting_updater_func_source_site
        )
        if processes.count() == 0:
            self.locked = False
            return None

        for process in processes:
            if (
                requesting_updater_func_type
                == novel_updater.NovelUpdaterType.NOVEL_PROFILER
            ):
                process_time = process.last_processed_by_novel_profiler
            elif (
                requesting_updater_func_type
                == novel_updater.NovelUpdaterType.NOVEL_CHAPTER_PROFILER
            ):
                process_time = process.last_processed_by_novel_chapter_profiler
            elif (
                requesting_updater_func_type
                == novel_updater.NovelUpdaterType.NOVEL_CHAPTER_UPDATER
            ):
                process_time = process.last_processed_by_novel_chapter_updater
            if (
                datetime.now(timezone.utc) - process_time
            ).seconds // 60 >= PROCESS_CONTROL_THRESHOLD:
                process.activate_process()
                self.locked = False
                return process
        self.locked = False
        return None


class NovelProcess(models.Model):
    created = models.DateTimeField(auto_now=True)
    pool = models.ForeignKey(
        NovelProcessPool, on_delete=models.CASCADE, related_name="processes"
    )
    novel_profile = models.OneToOneField(
        NovelProfile,
        on_delete=models.PROTECT,
        related_name="process",
        blank=True,
        null=True,
    )

    is_being_processed = models.BooleanField(default=False)
    last_processed_by_novel_profiler = models.DateTimeField()
    last_processed_by_novel_chapter_profiler = models.DateTimeField()
    last_processed_by_novel_chapter_updater = models.DateTimeField()
    source_site = models.CharField(max_length=256)
    base_link = models.CharField(max_length=8128)

    def activate_process(self):
        if self.is_being_processed:
            raise npexc.ProcessAlreadyActiveException(self.base_link)
        self.is_being_processed = True
        self.save()

    def release_process(self, releaser_updater_func_type):
        if not self.is_being_processed:
            raise npexc.ProcessAlreadyInactiveException(self.base_link)
        if releaser_updater_func_type == novel_updater.NovelUpdaterType.NOVEL_PROFILER:
            self.last_processed_by_novel_profiler = datetime.now(timezone.utc)
        elif (
            releaser_updater_func_type
            == novel_updater.NovelUpdaterType.NOVEL_CHAPTER_PROFILER
        ):
            self.last_processed_by_novel_chapter_profiler = datetime.now(timezone.utc)
        elif (
            releaser_updater_func_type
            == novel_updater.NovelUpdaterType.NOVEL_CHAPTER_UPDATER
        ):
            self.last_processed_by_novel_chapter_updater = datetime.now(timezone.utc)
        self.is_being_processed = False
        self.save()
