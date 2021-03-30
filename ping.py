#!/home/ducatlab/miniconda3/envs/env/bin python3
import cellpose
import omero, omero.scripts as scripts
client = scripts.client("ping.py", "simple ping script",
                        scripts.Long("a"), scripts.String("b"))

keys = client.getInputKeys()
print("Keys found:")
print(keys)
for key in keys:
      client.setOutput(key, client.getInput(key))
