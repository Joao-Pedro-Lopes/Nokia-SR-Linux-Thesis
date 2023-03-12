import json
import yaml
import sys

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
    if (node_name.startswith("leaf") or node_name.startswith("spine")):
        print(f"Node: {node_name}")
        # Extract comma-separated lists of interface names, subinterface indices, and IPv4 addresses
        interface_names = node_data['config']['vars']['interface'].split(',')
        subinterface_indices = [int(i) for i in node_data['config']['vars']['subinterface'].split(',')]
        ipv4_addresses = node_data['config']['vars']['ipv4-address'].split(',')
        
        # Loop through the interface names, subinterface indices, and IPv4 addresses, and fill in the templates
        for i, (interface_name, subinterface_index, ipv4_address) in enumerate(zip(interface_names, subinterface_indices, ipv4_addresses)):
            # Define the interface template as a dictionary for this interface
            interface_cfg_template = {
                "name": interface_name,
                "description": f"{interface_name} interface on {node_name} node",
                "admin_state": "enable",
                "subinterface": [],
            }

            # Define the subinterface template as a dictionary for this interface
            subinterface_cfg_template = {
                "index": subinterface_index,
                "admin-state": "enable",
                "ipv4": {
                    "address": [
                        {
                            "ip-prefix": ipv4_address
                        }
                    ]
                }
            }

            # Add the subinterface configuration to the interface configuration for this interface
            interface_cfg_template["subinterface"].append(subinterface_cfg_template)

            # Add the interface configuration to the dictionary for this node
            if node_name not in interface_configs:
                interface_configs[node_name] = {}
                interface_configs[node_name]["interface"] = []
            interface_configs[node_name]["interface"].append(interface_cfg_template)

# Loop through the interface configurations for each node and write them to separate files
for node_name, node_interfaces in interface_configs.items():
    output = json.dumps(node_interfaces, indent=4)
    filename = f"{node_name}_config.json"
    with open(f"../output/{filename}", "w") as f:
        f.write(output)
        print(f"Wrote interface configuration for {node_name} to {filename}")
