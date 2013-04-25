from django.db.models.loading import get_model
from rodan.utils import remove_prefixes


# These are not actual Django models
class JobBase:
    is_automatic = False
    outputs_image = True
    outputs_mei = False
    outputs_txt = False
    name = ''
    slug = ''
    description = ''
    template = ''
    """A dict of parameters to pass to a celery task"""
    parameters = {}
    """The celery task to execute"""
    task = None
    enabled = True
    """ True if this job requires all of the pages to be at this step
    before it is run (i.e. multi-page jobs) """
    all_pages = False

    def get_name(self):
        return self.name or remove_prefixes(self.__class__.__name__)

    def get_slug(self):
        """If the child class defines a slug, use that; otherwise, take the
        class name and just convert it to lowercase.
        """
        return self.slug or self.get_name().lower().replace(" ", "-")

    def get_context(self, page):
        """
        Override this if you want to pass custom variables to the template.
        Will be accessible in the template as "context" (so if you return
        {'blah': 'blah'}, then it's accessible through {{ context.blah }} in
        the template.
        """
        return {}

    def on_post(self, result_id, **kwargs):
        """
        If you want to perform a custom action after submit that is
        not a celery task, override this.
        In the case of a multi-page job, a list of result_ids will be passed
        into the result_id parameter.
        """
        self.task.delay(result_id, **kwargs)


class ManualJobBase(JobBase):
    def on_post(self, result_id, **kwargs):
        """
        Start the next automatic job.

        ManualJobBase should be used when there is no celery task required
        (and so there is no need to delay anything).
        """
        Result = get_model('rodan', 'Result')
        result = Result.objects.get(pk=result_id)
        result.page.start_next_automatic_job(result.user)


class JobType:
    """
    I will put in a nice descriptive docstring very very soon

    For now, note that all main types are prime and subtypes are multiples of
    the parent type.
    """
    IMAGE = 1
    BINARISED_IMAGE = 2
    POLYGON_JSON = 3
    CLASSIFY_XML = 4
    SEGMENTED_IMAGE = 5
    NEUME_IMAGE = 6
    NEUME_DESPECKLE_IMAGE = 11
    RANKED_IMAGE = 7
    MEI = 8
    SOLR = 9
    END = 10
    BORDER_REMOVE_IMAGE = 13
    STAFFGROUP_INPUT = 17
    ROTATED_IMAGE = 19
    CORRECTED_MEI = 23
    DESPECKLE_IMAGE = 29