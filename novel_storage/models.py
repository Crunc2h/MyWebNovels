from django.db import models
import enums_configs.models as ec_models


class TempNovelLink(models.Model):
    source_site = models.CharField(max_length=256)
    link = models.CharField(max_length=8128)


class NovelProfile(models.Model):
    name = models.CharField(max_length=1024)
    summary = models.TextField(max_length=16256)
    number_of_chapters = models.IntegerField()

    language = models.ForeignKey(
        ec_models.NovelLanguage,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="profiles",
    )
    completion_status = models.ForeignKey(
        ec_models.NovelCompletionStatus,
        on_delete=models.PROTECT,
        related_name="profiles",
    )
    author_name = models.ForeignKey(
        ec_models.Author, on_delete=models.PROTECT, related_name="profiles"
    )

    categories = models.ManyToManyField(
        ec_models.NovelCategory, related_name="profiles"
    )
    tags = models.ManyToManyField(ec_models.NovelTag, related_name="profiles")


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
