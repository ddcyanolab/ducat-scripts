import omero, omero.scripts as scripts
from omero.gateway import BlitzGateway, ColorHolder
from omero.model import MaskI
from omero.rtypes import (
    rdouble,
    rint,
    rstring,
    wrap,
)
import omero_rois
import omero
from getpass import getpass
from cellpose import models, utils,plot,io
import numpy as np

# Define the script name & description, and a single 'required' parameter
client = scripts.client("test-segment.py", "Get channel names and test segmentation",
                        scripts.Long("imageId", optional=False))

# get the Image Id from the parameters.
imageId = client.getInput("imageId", unwrap=True)   # unwrap the rtype

# Use the Python Blitz Gateway for convenience
conn = BlitzGateway(client_obj=client)

# get the Image, print its name
image = conn.getObject("Image", imageId)
print(image.getName())

# Print each channel 'label' (Name or Excitation wavelength)
for i, ch in enumerate(image.getChannels()):
    print(ch.getLabel())
    # Return as output. Key is string, value is rtype
    client.setOutput("Channel%s" % i, wrap(str(ch.getLabel())))

def find_chan(image,channel):

    """
    Finds the specified channel number from the image metadata
    """

    for i, chan in enumerate(image.getChannels()):
        #print(i, dic)
        if chan.getLabel() == channel:
            return i
    return -1

# get DsRed Channel
pixels = image.getPrimaryPixels()
dsred_channel = find_chan(image,'DsRed')
dsred = pixels.getPlane(0, dsred_channel, 0)
print(dsred.shape)

use_GPU = models.use_gpu()
print('>>> GPU activated? %d'%use_GPU)
# Cleanup
client.closeSession()
