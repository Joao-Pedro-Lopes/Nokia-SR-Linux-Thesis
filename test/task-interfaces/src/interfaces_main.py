import json
import yaml
import sys

from interface_generator import interface_generator
from bgp_generator import bgp_generator
from ibgp_generator import ibgp_generator

filename = sys.argv[-1]

# Open the file and load its contents into a dictionary
with open(filename, 'r') as f:
    data = yaml.safe_load(f)

# Create a dictionary to map each node to a list of interface configurations
interface_configs = {}

# Loop through each node and fill in the templates
for node_name, node_data in data.items():
    if (node_name.startswith('leaf') or node_name.startswith('spine')):
        print(f'Node: {node_name}')
        
        interface_generator(interface_configs, node_name, node_data) 

# Loop through the interface configurations for each node and write them to separate files
for node_name, node_interfaces in interface_configs.items():
    output = json.dumps(node_interfaces, indent=4)
    filename = f'{node_name}_interfaces.json'
    with open(f'output/interfaces/{filename}', 'w') as f: # --> change to output/interfaces/{filename} done on test environment
        f.write(output)
        print(f'Wrote interface configuration for {node_name} to {filename}')


