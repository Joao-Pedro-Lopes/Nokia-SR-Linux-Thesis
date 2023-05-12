def ibgp_generator(interface_configs, node_name, node_data, individual):
    config = {}
    if (individual):
        config[node_name] = {}
        config[node_name]['network-instance'] = []
        config[node_name]['network-instance'].append({})
    else:
        config[node_name] = interface_configs[node_name]

    #TODO: revision with peer-as and local-as
    peer_groups = [peer_g.strip() for peer_g in node_data['config']['vars']['ibgp-peer-group'].split(',')]
    neighbors = [n.strip() for n in node_data['config']['vars']['ibgp-neighbor'].split(',')]

    ibgp_group_template = {
        'group-name': node_data['config']['vars']['ibgp-group'],
        'export-policy': 'all', #node_data['config']['vars']['ibgp-export-policy']
        'import-policy': 'all', #node_data['config']['vars']['ibgp-import-policy']
        'peer-as': node_data['config']['vars']['ibgp-peer-as'],
        'ipv4-unicast': {
            "admin-state": 'disable'
        },
        'evpn': {
            'admin-state': 'enable'
        },
        'local-as': [
            {
                "as-number": ''
            }
        ],
        #'timers': {
            #'minimum-advertisement-interval': node_data['config']['vars']['ibgp-minimum-advertisement-interval']
        #},
        #'route-reflector': {
        #    'client': True,
        #    'cluster-id': '0.0.0.1'
        #}
    }

    if ('ibgp-route-reflector' in node_data['config']['vars'] and node_data['config']['vars']['ibgp-route-reflector']):
        ibgp_group_template['route-reflector'] = {}
        ibgp_group_template['route-reflector']['client'] = True
        ibgp_group_template['route-reflector']['cluster-id'] = node_data['config']['vars']['ibgp-cluster-id']

    peer_as = node_data['config']['vars']['ibgp-peer-as']
    peer_autonomous_systems = []
    if isinstance(peer_as, int):
        ibgp_group_template['local-as'][0]['as-number'] = peer_as
    elif isinstance(peer_as, str):
        peer_autonomous_systems = [peer_as.strip() for peer_as in peer_as.split(',')]

    if individual:
        config[node_name]['network-instance'][0]['name'] = "default"
        config[node_name]['network-instance'][0]['protocols'] = {}
        config[node_name]['network-instance'][0]['protocols']['bgp'] = {}
        config[node_name]['network-instance'][0]['protocols']['bgp']['group'] = []
        config[node_name]['network-instance'][0]['protocols']['bgp']['group'].append(ibgp_group_template)
    else:
        config[node_name]['network-instance'][0]['protocols']['bgp']['group'].append(ibgp_group_template)

    #TODO: check if this logic can be applied to iBGP
    if peer_autonomous_systems != []:
        for i, (peer_autonomous_system, peer_group, neighbor) in enumerate(zip(peer_autonomous_systems, peer_groups, neighbors)):
            #TODO: revision
            ibgp_neighbor_template = {
                "peer-address": neighbor,
                "peer-as": int(peer_autonomous_system),
                "peer-group": peer_group
            }

            if individual:
                config[node_name]['network-instance'][0]['protocols']['bgp']['neighbor'] = []
                config[node_name]['network-instance'][0]['protocols']['bgp']['neighbor'].append(ibgp_neighbor_template)
            else:
                config[node_name]['network-instance'][0]['protocols']['bgp']['neighbor'].append(ibgp_neighbor_template)
    else:
        for i, (peer_group, neighbor) in enumerate(zip(peer_groups, neighbors)):
            ibgp_neighbor_template = {
                'peer-address': neighbor,
                'admin-state': 'enable',
                'peer-group': peer_group,
                'transport': {
                    'local-address': node_data['config']['vars']['ibgp-local-address']
                }
            }

            if individual:
                config[node_name]['network-instance'][0]['protocols']['bgp']['neighbor'] = []
                config[node_name]['network-instance'][0]['protocols']['bgp']['neighbor'].append(ibgp_neighbor_template)
            else:
                config[node_name]['network-instance'][0]['protocols']['bgp']['neighbor'].append(ibgp_neighbor_template)
    
    return config