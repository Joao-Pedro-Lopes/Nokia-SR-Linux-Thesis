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

# Extract the vars section
vars_section = data['topology']['nodes']

# Create a dictionary to map each node to a list of interface configurations
interface_configs = {}

# Loop through each node and fill in the templates
for node_name, node_data in vars_section.items():
    if (node_name.startswith('leaf') or node_name.startswith('spine')):
        print(f'Node: {node_name}')
        
        interface_generator(interface_configs, node_name, node_data) 

        if 'bgp-underlay' in node_data['config']['vars'] and node_data['config']['vars']['bgp-underlay']:

            bgp_generator(interface_configs, node_name, node_data)
        
        if 'ibgp-overlay' in node_data['config']['vars'] and node_data['config']['vars']['ibgp-overlay']:

            ibgp_generator(interface_configs, node_name, node_data)

        if 'routing-policy' in node_data['config']['vars']:
            interface_configs[node_name]['routing-policy'] = {
                'policy': [
                    {
                        'name': node_data['config']['vars']['routing-policy'],
                        'default-action': {
                            'policy-result': node_data['config']['vars']['routing-policy-action']
                        }
                    }
                ]
            }

# Loop through the interface configurations for each node and write them to separate files
for node_name, node_interfaces in interface_configs.items():
    output = json.dumps(node_interfaces, indent=4)
    filename = f'{node_name}_config.json'
    with open(f'output/{filename}', 'w') as f: # --> change to output/{filename} done on test environment
        f.write(output)
        print(f'Wrote interface configuration for {node_name} to {filename}')


#TODO: FIX ROUTING POLICY AND MISSING iBGP with route reflector
