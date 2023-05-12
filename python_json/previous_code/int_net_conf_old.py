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
        # Also removes unwanted spaces from the new generated variables
        interface_names = [name.strip() for name in node_data['config']['vars']['interface'].split(',')]
        subinterface_indices = [int(i) for i in node_data['config']['vars']['subinterface'].split(',')]
        ipv4_addresses = [addr.strip() for addr in node_data['config']['vars']['ipv4-address'].split(',')]
        network_instances = [instance.strip() for instance in node_data['config']['vars']['network-instance'].split(',')]
                
        # Loop through the interface names, subinterface indices, and IPv4 addresses, and fill in the templates
        for i, (interface_name, subinterface_index, ipv4_address, network_instance) in enumerate(zip(interface_names, subinterface_indices, ipv4_addresses, network_instances)):
            # Define the interface template as a dictionary for this interface
            interface_cfg_template = {
                "name": interface_name.strip(),
                "description": f"{interface_name.strip()} interface on {node_name.strip()} node",
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

            # Define the network-instance template as a dictionary for this interface
            network_instance_template = {
                "name": network_instance,
                "interface": [
                    {
                    "name": interface_name + "." + str(subinterface_index)
                    }
                ]
            }

            # Add the subinterface configuration to the interface configuration for this interface
            interface_cfg_template["subinterface"].append(subinterface_cfg_template)

            # Add the interface configuration to the dictionary for this node
            if node_name not in interface_configs:
                interface_configs[node_name] = {}
                interface_configs[node_name]["interface"] = []
                interface_configs[node_name]["network-instance"] = []
            interface_configs[node_name]["interface"].append(interface_cfg_template)
            interface_configs[node_name]["network-instance"].append(network_instance_template)
        
        """ peer_as = node_data['config']['vars']['peer-as']
        if isinstance(peer_as, int):
            peer_autonomous_systems = [str(peer_as)]
        elif isinstance(peer_as, str):
            peer_autonomous_systems = [peer_as.strip() for peer_as in peer_as.split(',')]
        #peer_autonomous_systems = [peer_as.strip() for peer_as in node_data['config']['vars']['peer-as'].split(',')]
        neighbors = [n.strip() for n in node_data['config']['vars']['neighbor'].split(',')]

        if node_data['config']['vars']['bgp_underlay']:
            interface_configs[node_name]["network-instance"]["protocols"] = {}
            
            bgp_underlay_template = {
                "autonomous-system": node_data['config']['vars']['bgp_underlay'],
                "router-id": "10.0.0.1",
                "group": [
                {
                    "group-name": "eBGP-underlay",
                    "export-policy": node_data['config']['vars']['export-policy'],
                    "import-policy": node_data['config']['vars']['import-policy'],
                    "peer-as": 0 # 0 as default value 
                }
                ],
                "ipv4-unicast": {
                    "admin-state": "enable"
                },
                "neighbor": [
                    {
                        "peer-address": "",
                        "peer-group": ""
                    }
                ]
            }
            
            for i, (peer_autonomous_systems, neighbor) in enumerate(zip(peer_autonomous_systems, neighbors)):
                print(peer_autonomous_systems, neighbor) """
            

# Loop through the interface configurations for each node and write them to separate files
for node_name, node_interfaces in interface_configs.items():
    output = json.dumps(node_interfaces, indent=4)
    filename = f"{node_name}_config.json"
    with open(f"../output/{filename}", "w") as f:
        f.write(output)
        print(f"Wrote interface configuration for {node_name} to {filename}")
