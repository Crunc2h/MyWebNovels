import novel_scraper.native.novel_updater as novel_updater
import novel_scraper.native.ns_exceptions as nsexc
from novel_scraper.native.novel_ppool_cfg import PROCESS_CONTROL_THRESHOLD
from datetime import datetime, timezone, timedelta
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class NovelProfile(models.Model):
    name = models.CharField(max_length=1024)
    summary = models.TextField(max_length=16256)
    number_of_chapters = models.IntegerField()

    language = models.ForeignKey(
        NovelLanguage,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="profiles",
    )
    completion_status = models.ForeignKey(
        NovelCompletionStatus, on_delete=models.PROTECT, related_name="profiles"
    )
    author_name = models.ForeignKey(
        Author, on_delete=models.PROTECT, related_name="profiles"
    )

    categories = models.ManyToManyField(NovelCategory, related_name="profiles")
    tags = models.ManyToManyField(NovelTag, related_name="profiles")


class ChapterProfile(models.Model):
    name = models.CharField(max_length=1024)
    link = models.CharField(max_length=8128)
    number = models.CharField(max_length=64)
    source_update_time = models.CharField(max_length=512)
    already_exists = models.BooleanField(default=False)

    novel_profile = models.ForeignKey(
        NovelProfile,
        on_delete=models.CASCADE,
        related_name="chapter_profiles",
        blank=True,
        null=True,
    )


class ChapterText(models.Model):
    text = models.TextField(max_length=65024)

    chapter_profile = models.OneToOneField(
        ChapterProfile, on_delete=models.CASCADE, related_name="chapter_text"
    )
