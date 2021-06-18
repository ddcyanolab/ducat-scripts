# A list of datasets will be dynamically generated and used to populate the
# script parameters every time the script is called

import omero
import omero.gateway
from omero import scripts
import omero.util.script_utils as script_utils
from omero.rtypes import (
    rdouble,
    rint,
    rstring,
    wrap,
    rlong,
    robject,
)
def get_params():
    try:
        client = omero.client()
        client.createSession()
        conn = omero.gateway.BlitzGateway(client_obj=client)
        conn.SERVICE_OPTS.setOmeroGroup(-1)
        objparams = [rstring('Dataset:%d %s' % (d.id, d.getName()))
                     for d in conn.getObjects('Dataset')]
        if not objparams:
            objparams = [rstring('<No objects found>')]
        return objparams
    except Exception as e:
        return ['Exception: %s' % e]
    finally:
        client.closeSession()

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

def runScript():
    """
    The main entry point of the script
    """

    #objparams = get_params()
    dataTypes = [rstring('Dataset'),rstring('Image')]

    client = scripts.client(
        'get_channels.py', "Get channels from images",
        scripts.String("Data_Type", optional=False, grouping="01", values=dataTypes, default="Dataset"),
        scripts.List("IDs", optional=False, grouping="02").ofType(rlong(0))
        )
"""     client = scripts.client(
        'get_channels.py', 'Example script using dynamic parameters',

        scripts.String(
            'Dataset', optional=False, grouping='1',
            description='Select a dataset', values=objparams),

        namespaces=[omero.constants.namespaces.NSDYNAMIC],
    ) """

    try:
        scriptParams = client.getInputs(unwrap=True)
        message = 'Params: %s\n' % scriptParams
        print(message)
        client.setOutput('Message', rstring(str(message)))

    finally:
        client.closeSession()


if __name__ == '__main__':
    runScript()