def interface_generator(interface_configs, node_name, node_data):
    # Extract comma-separated lists of interface names, subinterface indices, and IPv4 addresses
    # Also removes unwanted spaces from the new generated variables
    interface_names = [name.strip() for name in node_data['config']['vars']['interface'].split(',')]
    subinterface_indices = [int(i) for i in node_data['config']['vars']['subinterface'].split(',')]
    ipv4_addresses = [addr.strip() for addr in node_data['config']['vars']['ipv4-address'].split(',')]
    #network_instances = [instance.strip() for instance in node_data['config']['vars']['network-instance'].split(',')]
            
    # Define the network-instance template as a dictionary for this interface
    network_instance_template = {
        'name': node_data['config']['vars']['network-instance'],
        'interface': [],
        'protocols': {}
    }
    
    # Loop through the interface names, subinterface indices, and IPv4 addresses, and fill in the templates
    for i, (interface_name, subinterface_index, ipv4_address) in enumerate(zip(interface_names, subinterface_indices, ipv4_addresses)):
        # Define the interface template as a dictionary for this interface
        interface_cfg_template = {
            'name': interface_name.strip(),
            'description': f'{interface_name.strip()} interface on {node_name.strip()} node',
            'admin-state': 'enable',
            'subinterface': [],
        }

        # Define the subinterface template as a dictionary for this interface
        subinterface_cfg_template = {
            'index': subinterface_index,
            'admin-state': 'enable',
            'ipv4': {
                'address': [
                    {
                        'ip-prefix': ipv4_address
                    }
                ]
            }
        }

        # Add the subinterface configuration to the interface configuration for this interface
        interface_cfg_template['subinterface'].append(subinterface_cfg_template)

        # Define the network instance interface template as a dictionary
        network_instance_interface_template = {
            'name': interface_name + '.' + str(subinterface_index)
        }

        # Add the interface configuration to the dictionary for this node
        if node_name not in interface_configs:
            interface_configs[node_name] = {}
            interface_configs[node_name]['interface'] = []
            interface_configs[node_name]['network-instance'] = []
            interface_configs[node_name]['network-instance'].append(network_instance_template)
        interface_configs[node_name]['interface'].append(interface_cfg_template)

        # Should need a fix, index must not be hardcoded
        interface_configs[node_name]['network-instance'][0]['interface'].append(network_instance_interface_template)

    return interface_configs