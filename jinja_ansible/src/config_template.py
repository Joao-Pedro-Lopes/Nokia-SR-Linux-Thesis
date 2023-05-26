def config_template(config_type, node, config):
    if config_type == 'interfaces':
        # Gather interface variables
        interfaces = []
        for interface in config['config']['vars']['interfaces']:
            interface_variable = {
                'interface-name': interface.get('interface-name', ''),
                'ip-address-p2p': interface.get('ip-address-p2p', ''),
            }
            interfaces.append(interface_variable)
        
        return {
            'interfaces': interfaces,
        }
    else:
        return None



"""def config_template(config_type, node, config):
    print(config_type)
    print(node)
    print(config)
    if config_type == 'interfaces':
        return {
            'node': node,
            'interface-name': config['config']['vars'].get('interface-name', ''),
            'ip-address-p2p': config['config']['vars'].get('ip-address-p2p', ''),
            'ip-address-loopback': config['config']['vars'].get('ip-address-loopback', '')
        }
    elif config_type == 'ebgp':
        return {
            'node': node,
            'autonomous-system': config['config']['vars'].get('autonomous-system', ''),
            'router-id': config['config']['vars'].get('router-id', ''),
            'peer-as': config['config']['vars'].get('peer-as', ''),
            'peer-address': config['config']['vars'].get('peer-address', '')
        }
    else:
        return None"""