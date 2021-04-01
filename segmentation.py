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

def process_images(conn, parameter_map):
    """
    Process the script params to make a list of channel_offsets, then iterate
    through the images creating a new image from each with the specified
    channel offsets
    """

    message = ""

    # Get the images
    images, log_message = script_utils.get_objects(conn, parameter_map)
    message += log_message
    if not images:
        return None, None, message
    image_ids = [i.getId() for i in images]
    return images,  message

# load
def load_images(conn, image_id):
    """
    Load the images in the specified dataset
    :param conn: The BlitzGateway
    :param dataset_id: The dataset's id
    :return: The Images or None
    """
    dataset = conn.getObject("Dataset", dataset_id)
    images = []
    if dataset is None:
        return None
    for image in dataset.listChildren():
        images.append(image)
    if len(images) == 0:
        return None

    for image in images:
        print("---- Processing image", image.id)
    return images

def get_image_list(conn,parameter_map):
    """
    Load the images in the specified dataset
    :param conn: The BlitzGateway
    :param parameter_map: The dataset's id
    :return: The Images or None
    """
    # Get images or datasets
    message = ""
    objects, log_message = script_utils.get_objects(conn, parameter_map)
    message += log_message
    if not objects:
        return None, message


    data_type = parameter_map["Data_Type"]
    if data_type == "Image":
        image_ids = [image.id for image in objects]
        #[image.id for image in objects]
    else:
        for dataset in objects:
            images = list(dataset.listChildren())
            if not images:
                continue
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



        #script_params = client.getInputs(unwrap=True)


        # wrap client to use the Blitz Gateway
        conn = BlitzGateway(client_obj=client)

        #images, message = get_image_list(conn, script_params)

        images,message= get_image_list(conn, parameter_map)
        for image in images:
            print(image)
        # Return message, new image and new dataset (if applicable) to the
        # client
    #    client.setOutput("Message", rstring(message))
    #    if len(images) == 1:
        #    client.setOutput("Image", robject(images[0]._obj))






        # Return message, new image and new dataset (if applicable) to the
        # client
        client.setOutput("Message", rstring(message))

    finally:
        client.closeSession()
if __name__ == "__main__":
    run_script()
