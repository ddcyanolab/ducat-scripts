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
def get_images(conn, script_params):
    data_type = parameter_map["Data_Type"]
    if data_type == "Image":
        dataset = None
        objects.sort(key=lambda x: (x.getName()))    # Sort images by name
        image_ids = [image.id for image in objects]



    else:
        for dataset in objects:
            images = list(dataset.listChildren())
            if not images:
                continue
            images.sort(key=lambda x: (x.getName()))
            image_ids = [i.getId() for i in images]
            new_img, link = make_single_image(services, parameter_map,
                                              image_ids, dataset, colour_map)
            if new_img:
                output_images.append(new_img)
            if link:
                links.append(link)

def run_script():
    """
    The main entry point of the script, as called by the client via the
    scripting service, passing the required parameters.
    """
    data_types = [rstring('Dataset'), rstring('Image')]
    try:

        client = scripts.client(
            'selectImageId.py',
            """Create new Images from existing images.
        See http://help.openmicroscopy.org/scripts.html""",

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