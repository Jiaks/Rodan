import utils
import gamera

from rodan.models.jobs import JobType, JobBase
from barfinder_resources.barfinder import BarlineFinder
from barfinder_resources.meicreate import BarlineDataConverter

@utils.rodan_task(inputs='tiff')
def barfinder(image_filepath, **kwargs):
    input_image = gamera.core.load_image(image_filepath)

    sg_hint = '(2|)x2 (4(2|))'

    bar_finder = BarlineFinder()
    staff_bb, bar_bb = bar_finder.process_file(input_image, sg_hint)
    
    bar_converter = BarlineDataConverter(staff_bb, bar_bb)
    bar_converter.bardata_to_mei(sg_hint)
    mei_file = bar_converter.get_wrapped_mei()

    return {
        'mei': mei_file
    }

class BarFinder(JobBase):
    slug = 'bar-finder'
    input_type = JobType.ROTATED_IMAGE
    output_type = JobType.MEI
    description = 'Find the bars in an image'
    name = 'Bar Finder'
    is_automatic = True
    show_during_wf_create = True
    parameters = {
    }
    task = barfinder
    outputs_image = False