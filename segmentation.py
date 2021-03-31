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
)
import omero_rois
from cellpose import models, utils,plot,io
import numpy as np
from skimage.measure import label



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
