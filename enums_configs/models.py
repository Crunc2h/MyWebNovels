from django.db import models


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
