from gamera.core import init_gamera
init_gamera()
from rodan.jobs.gamera.base import load_gamera_module

from rodan.jobs import module_loader

module_loader('gamera.plugins.binarization', load_gamera_module)
module_loader('gamera.plugins.threshold', load_gamera_module)
module_loader('gamera.plugins.image_conversion', load_gamera_module)
module_loader('gamera.plugins.transformation', load_gamera_module)
module_loader('gamera.toolkits.background_estimation.plugins.background_estimation', load_gamera_module)
module_loader('gamera.toolkits.border_removal.plugins.border_removal', load_gamera_module)
module_loader('gamera.toolkits.lyric_extraction.plugins.border_lyric', load_gamera_module)
module_loader('gamera.toolkits.lyric_extraction.plugins.lyricline', load_gamera_module)
module_loader('gamera.toolkits.lyric_extraction.plugins.lyric_extractor', load_gamera_module)
module_loader('gamera.toolkits.musicstaves.plugins.musicstaves_plugins', load_gamera_module)
module_loader('gamera.toolkits.staffline_removal.plugins.staff_removal', load_gamera_module)
module_loader('gamera.toolkits.rodan_plugins.plugins.rdn_despeckle', load_gamera_module)


module_loader('rodan.jobs.gamera.interactive_tasks.pixel_segment')
module_loader('rodan.jobs.gamera.interactive_tasks.poly_mask')
module_loader('rodan.jobs.gamera.interactive_tasks.rdn_rotate')
module_loader('rodan.jobs.gamera.interactive_tasks.rdn_despeckle')
module_loader('rodan.jobs.gamera.interactive_tasks.rdn_crop')
module_loader('rodan.jobs.gamera.interactive_tasks.segmentation.tasks')


module_loader('rodan.jobs.gamera.auto_tasks.border_removal')
module_loader('rodan.jobs.gamera.auto_tasks.pitch_finding.pitch_finding')
module_loader('rodan.jobs.gamera.auto_tasks.staff_removal')
