from django.db import models
from django.conf import settings
from rodan.models.project import Project
from django.contrib.auth.models import User
from uuidfield import UUIDField

import os


class Page(models.Model):
    def upload_path(self, filename):
        return os.path.join("projects", str(self.project.uuid), "pages", str(self.uuid), filename)

    uuid = UUIDField(primary_key=True, auto=True)
    project = models.ForeignKey(Project, related_name="pages")
    page_image = models.FileField(upload_to=upload_path, null=True)
    page_order = models.IntegerField(null=True)
    image_file_size = models.IntegerField(null=True)  # in bytes

    creator = models.ForeignKey(User, related_name="pages", null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'rodan'

    def __unicode__(self):
        return unicode(self.page_image.name)

    def _thumb_filename(self, path, size):
        base_path, _ = os.path.splitext(path)
        return "{0}_{1}.{2}".format(base_path, size, settings.THUMBNAIL_EXT)

    def _thumb_path(self, size):
        return os.path.join("projects/{0}/pages/{1}/thumbnails/".format(self.project.uuid, self.uuid),
                            self._thumb_filename(self.filename, size))

    def thumb_path(self, size=settings.SMALL_THUMBNAIL):
        return os.path.join(settings.MEDIA_ROOT,
                            self._thumb_path(size=size))

    @property
    def image_path(self):
        return self.page_image.path

    @property
    def filename(self):
        return os.path.basename(self.image_path)

    @property
    def small_thumb_url(self):
        return os.path.join(settings.MEDIA_URL, self._thumb_path(size=settings.SMALL_THUMBNAIL))

    @property
    def medium_thumb_url(self):
        return os.path.join(settings.MEDIA_URL, self._thumb_path(size=settings.MEDIUM_THUMBNAIL))

    @property
    def large_thumb_url(self):
        return os.path.join(settings.MEDIA_URL, self._thumb_path(size=settings.LARGE_THUMBNAIL))