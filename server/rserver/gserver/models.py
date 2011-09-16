from django.db import models
from uuidfield import UUIDField

import urllib2
import os
from gamera.core import *
from gamera import plugin
init_gamera()

# development -- logging & debugging
import logging
lg = logging.getLogger('gserver.models')
f = logging.Formatter("%(levelname)s %(asctime)s On Line: %(lineno)d %(message)s")
h = logging.StreamHandler()
h.setFormatter(f)
lg.setLevel(logging.DEBUG)
lg.addHandler(h)


class Image(models.Model):
    url = models.URLField()
    id = UUIDField(auto = True, primary_key = True)
    localpath = models.CharField(max_length = 255)
    pixel_type = models.IntegerField(max_length = 1, null = True)
    
    def __unicode__(self):
        return u"\nURL:{0} \nID:{1} \nPIXEL TYPE:{2} \nLOCAL PATH:{3}".format(
            self.url, self.id, self.pixel_type, self.localpath)

    def save(self, *args, **kwargs):

        super(Image, self).save(*args, **kwargs)   # This one stores the ID to be used afterwards  

        lg.debug("Saving Image ID:{0}".format(self.id))
        image_folder = os.path.join("images", self.id)
        if os.path.exists(image_folder) is not True:
            os.mkdir(image_folder)
        extension = os.path.splitext(self.url)[-1]
        self.localpath = os.path.join(image_folder, (self.id + extension))

        u = urllib2.urlopen(self.url)
        f = open(self.localpath, 'w')
        f.write(u.read())
        f.close()
        image = load_image(self.localpath)
        self.pixel_type = image.data.pixel_type

        # print "\nIMAGE: {0}".format(self)
        # print "\nAVAILABLE PLUGINS: {0}".format(
        #     plugin.plugin_methods[self.pixel_type].keys())
        
        super(Image, self).save(*args, **kwargs)

class ImageTransformation(models.Model):
    image = models.ForeignKey(Image)    # There is an unique set of image transformation according to the image type
    img_transformation = models.CharField(max_length = 255)
    id = UUIDField(auto = True, primary_key = True)

    def available_plugins(self):
        # print "LOCAL PATH: {0}".format(Image.objects.get(id = self.image_id).localpath)
        image_ = load_image(Image.objects.get(id = self.image_id).localpath)
        pixel_type = image_.data.pixel_type
        plugins = plugin.plugin_methods[pixel_type].keys()
        lg.debug("\nAvailable plugins for this image: \n{0}".format (plugins))

    def __unicode__(self):
        return u"\nTransformation:{0} \nID:{1} \nImage:{2}".format(
            self.img_transformation, self.id, self.image)




# i = Image(url = "http://www.vigliensoni.com/resources/vigliensoni_com.png")