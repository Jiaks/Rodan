import os
import shutil
from django.db import models
from django_extensions.db.fields import json
from uuidfield import UUIDField


class RunJobStatus(object):
    NOT_RUNNING = 0
    RUNNING = 1
    WAITING_FOR_INPUT = 2
    RUN_ONCE_WAITING = 3
    HAS_FINISHED = 4
    FAILED = -1


class RunJob(models.Model):
    """
        A RunJob is a job that has been executed as part of a Workflow Run. Every Result
        object is associated with a RunJob, since it is by the execution of this job that
        each result is produced.

        A RunJob keeps track of the settings that were used to produce the result image.

        The "needs_input" parameter is key to the functioning of interactive jobs. Each celery task
        should retrieve its associated runjob just prior to executing the job. If it sees a True value
        for `needs_input`, it will fall out of the queue and schedule itself for retrying after a set period.
        (By default, 3 minutes)
    """
    STATUS_CHOICES = [(RunJobStatus.NOT_RUNNING, "Not Running"),
                      (RunJobStatus.RUNNING, "Running"),
                      (RunJobStatus.WAITING_FOR_INPUT, "Waiting for input"),
                      (RunJobStatus.RUN_ONCE_WAITING, "Run once, waiting for input"),
                      (RunJobStatus.HAS_FINISHED, "Has finished"),
                      (RunJobStatus.FAILED, "Failed, ZOMG")]

    @property
    def runjob_path(self):
        return os.path.join(self.workflow_run.workflow_run_path, "{0}_{1}".format(self.workflow_job.sequence, str(self.pk)))

    class Meta:
        app_label = 'rodan'
        ordering = ['workflow_job__sequence']

    uuid = UUIDField(primary_key=True, auto=True)
    workflow_run = models.ForeignKey("rodan.WorkflowRun", related_name="run_jobs")
    workflow_job = models.ForeignKey("rodan.WorkflowJob")
    page = models.ForeignKey("rodan.Page")

    job_settings = json.JSONField(blank=True, null=True)
    needs_input = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<RunJob {0} {1} ({2})>".format(str(self.uuid), self.workflow_job.job.job_name, self.needs_input)

    def save(self, *args, **kwargs):
        super(RunJob, self).save(*args, **kwargs)
        if not os.path.exists(self.runjob_path):
            os.makedirs(self.runjob_path)

    def delete(self, *args, **kwargs):
        if os.path.exists(self.runjob_path):
            shutil.rmtree(self.runjob_path)
        super(RunJob, self).delete(*args, **kwargs)

    @property
    def sequence(self):
        return self.workflow_job.sequence

    @property
    def job_name(self):
        return self.workflow_job.job_name

    @property
    def page_name(self):
        return self.page.name