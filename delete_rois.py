"""
This is an OMERO server-side script to perform bulk deletion of mask roi annotations.
"""

# import required packages
import omero, omero.scripts as scripts
from omero.gateway import BlitzGateway
from omero.rtypes import (
    rdouble,
    rint,
    rstring,
    wrap,
    rlong,
    robject,
)

import omero.util.script_utils as script_utils





def delete_rois(conn,image_ids):
    """
    Delete all ROIs from an image
    """
    n = 0
    for imageId in image_ids:
        roi_service = conn.getRoiService()
        result = roi_service.findByImage(imageId, None)
        roi_ids = [roi.id.val for roi in result.rois]
        if roi_ids != []:
            conn.deleteObjects("Roi", roi_ids)
            n+=1
    message = str(n) + ' images'
    return message

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
        'Delete_masks.py',
        """Bulk deletion of segmentation masks""",

        scripts.String(
            "Data_Type", optional=False, grouping="1",
            description="Use all the images in specified 'Datasets' or choose"
            " individual 'Images'.", values=data_types, default="Image"),

        scripts.List(
            "IDs", optional=False, grouping="2",
            description="List of Dataset IDs or Image IDs to "
            "process.").ofType(rlong(0)),


        authors=["Jonathan Sakkos"],
        institutions=["Michigan State University"],
        contact="sakkosjo@msu.edu",

    )

    try:
        parameter_map = client.getInputs(unwrap=True)
        # wrap client to use the Blitz Gateway
        conn = BlitzGateway(client_obj=client)
        images,message= get_image_list(conn, parameter_map)
        msg = delete_rois(conn,images)
        client.setOutput('Processed',wrap(msg))

    finally:
        client.closeSession()
if __name__ == "__main__":
    run_script()
