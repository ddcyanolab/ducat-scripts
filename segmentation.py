"""
This is an OMERO server-side script that uses Cellpose for cell segmentation.
"""

# import required packages
import omero, omero.scripts as scripts
from omero.gateway import BlitzGateway, ColorHolder
from omero.model import MaskI
from omero.rtypes import (
    rdouble,
    rint,
    rstring,
    wrap,
    rlong,
    robject,
)
import omero.constants
import omero.util.script_utils as script_utils
import omero_rois
from cellpose import models, utils,plot,io
import numpy as np
from skimage.measure import label

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
def check_for_mask(conn,imageId):
    ImageMask = False
    roi_service = conn.getRoiService()
    result = roi_service.findByImage(imageId, None)
    for roi in result.rois:
        for i,s in enumerate(roi.copyShapes()):
            if type(s) == omero.model.MaskI:
                ImageMask = True
                break
    return ImageMask
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

def segment_images(client,conn, image_ids):
    """
    Load images, segment cells using Cellpose, return masks as OMERO ROIs
    """
    # check if CUDA is enabled
    use_GPU = models.use_gpu()
    print('>>> GPU activated? %d'%use_GPU)
    if use_GPU == 1 or True:
        GPUmessage = '>>> GPU activated'
    else:
        GPUmessage = '>>> GPU not activated'
    client.setOutput(rstring(GPUmessage))
    seg_chan_name = parameter_map["Segmentation_Channel"]
    #client.setOutput("Channel%s" % i, wrap(str(ch.getLabel())))
    client.setOutput(rstring('Segmentation Channel:')+rstring(seg_chan_name))

    #load cellpose model
    model = models.Cellpose(gpu=use_GPU,model_type='cyto')
    message = ""
    for imageId in image_ids:
        image = conn.getObject("Image", imageId)
        print("---- Processing image ", image.getId(), image.getName())
        ImageMask = check_for_mask(conn,imageId)
        if ImageMask == False:
            pixels = image.getPrimaryPixels()
            seg_chan_num = find_chan(image,seg_chan)
            seg_chan_pixels = pixels.getPlane(0, seg_chan_num, 0)
            masks, flows, styles, diams = model.eval(seg_chan_pixels, diameter=20,flow_threshold=0)
            # create segmentation roi
            updateService = conn.getUpdateService()
            msks = omero_rois.masks_from_label_image(label(masks))
            create_roi(image,msks)
        else:
            print('already contains a mask')
    return

def get_image_list(conn,parameter_map):
    """
    Gets image IDs from the list of images or dataset
    :param conn: The BlitzGateway
    :param parameter_map: The dataset's id
    :return: image IDs or None
    """
    # Get images or datasets
    message = ""
    objects, log_message = script_utils.get_objects(conn, parameter_map)
    message += log_message
    if not objects:
        return None, message


    data_type = parameter_map["Data_Type"]
    if data_type == "Image":
        objects.sort(key=lambda x: (x.getName()))    # Sort images by name
        image_ids = [image.id for image in objects]
        #[image.id for image in objects]
    else:
        for dataset in objects:
            images = list(dataset.listChildren())
            if not images:
                continue
            images.sort(key=lambda x: (x.getName()))
            image_ids = [i.getId() for i in images]

    return image_ids, message

def run_script():
    """
    The main entry point of the script, as called by the client via the
    scripting service, passing the required parameters.
    """
    data_types = [rstring('Dataset'), rstring('Image')]

    client = scripts.client(
        'Segment_Cells.py',
        """Segment cells using Cellpose""",

        scripts.String(
            "Data_Type", optional=False, grouping="1",
            description="Use all the images in specified 'Datasets' or choose"
            " individual 'Images'.", values=data_types, default="Image"),

        scripts.List(
            "IDs", optional=False, grouping="2",
            description="List of Dataset IDs or Image IDs to "
            "process.").ofType(rlong(0)),

        scripts.String(
            "Segmentation_Channel", optional=True, grouping="3",
            default='DsRed',
            description="Channel to use for cell segmentation"),


    )

    try:
        parameter_map = client.getInputs(unwrap=True)
        # wrap client to use the Blitz Gateway
        conn = BlitzGateway(client_obj=client)
        images,message= get_image_list(conn, parameter_map)
        segment_images(client,conn,images)
        message = 'Processed ' + str(len(images)) + ' images'
        # Return message, new image and new dataset (if applicable) to the
        # client
        client.setOutput(rstring(message))

    finally:
        client.closeSession()
if __name__ == "__main__":
    run_script()
