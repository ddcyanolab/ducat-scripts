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
from cellpose import models, utils,plot,io
import numpy as np
from skimage.measure import label
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
# function to find a specific channel by name
def find_chan(image,channel):

    """
    Finds the specified channel number from the image metadata
    """

    for i, chan in enumerate(image.getChannels()):
        #print(i, dic)
        if chan.getLabel() == channel:
            return i
    return -1
# We have a helper function for creating an ROI and linking it to new shapes
def create_roi(img, shapes):
    # create an ROI, link it to Image
    roi = omero.model.RoiI()
    # use the omero.model.ImageI that underlies the 'image' wrapper
    roi.setImage(img._obj)
    for shape in shapes:
        roi.addShape(shape)
    # Save the ROI (saves any linked shapes too)
    return updateService.saveAndReturnObject(roi)
# get DsRed Channel
pixels = image.getPrimaryPixels()
dsred_channel = find_chan(image,'DsRed')
dsred = pixels.getPlane(0, dsred_channel, 0)
print(dsred.shape)

use_GPU = models.use_gpu()
print('>>> GPU activated? %d'%use_GPU)

# segment cell
model = models.Cellpose(gpu=use_GPU,model_type='cyto')

ImageMask = False

roi_service = conn.getRoiService()
result = roi_service.findByImage(image.getId(), None)
for roi in result.rois:
    for i,s in enumerate(roi.copyShapes()):
        if type(s) == omero.model.MaskI:
            ImageMask = True
            break
# Segment
if ImageMask == False:
    masks, flows, styles, diams = model.eval(dsred, diameter=20,flow_threshold=0)

    # create segmentation roi
    updateService = conn.getUpdateService()
    msks = omero_rois.masks_from_label_image(label(masks))
    create_roi(image,msks)
else:
    print('already contains a mask')

# Cleanup
client.closeSession()
