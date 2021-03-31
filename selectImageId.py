import re
from numpy import zeros

import omero
import omero.scripts as scripts
from omero.gateway import BlitzGateway
import omero.constants
from omero.rtypes import rstring, rlong, robject
import omero.util.script_utils as script_utils

def process_images(conn, script_params):
    """
    Process the script params to make a list of channel_offsets, then iterate
    through the images creating a new image from each with the specified
    channel offsets
    """

    message = ""

    # Get the images
    images, log_message = script_utils.get_objects(conn, script_params)
    message += log_message
    if not images:
        return None, None, message
    image_ids = [i.getId() for i in images]
    return images, dataset, message


def run_script():
    """
    The main entry point of the script, as called by the client via the
    scripting service, passing the required parameters.
    """

    try:

        client = scripts.client(
            'selectImageId.py',
            """Create new Images from existing images.
        See http://help.openmicroscopy.org/scripts.html""",

            scripts.String(
                "Data_Type", optional=False, grouping="1",
                description="Pick Images by 'Image' ID or by the ID of their "
                "Dataset'", values=data_types, default="Image"),

            scripts.List(
                "IDs", optional=False, grouping="2",
                description="List of Dataset IDs or Image IDs to "
                "process.").ofType(rlong(0)),

            scripts.Bool(
                "Segmentation_Channel", grouping="3", default=True,
                description="Choose to include this channel in the output image"),


        )


        script_params = client.getInputs(unwrap=True)
        print(script_params)

        # wrap client to use the Blitz Gateway
        conn = BlitzGateway(client_obj=client)

        images, dataset, message = process_images(conn, script_params)
        print(message)




        # Return message, new image and new dataset (if applicable) to the
        # client
        client.setOutput("Message", rstring(message))

    finally:
        client.closeSession()
if __name__ == "__main__":
    run_script()
