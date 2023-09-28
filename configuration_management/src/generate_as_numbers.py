def generate_as_numbers(data, as_range, neighbors_bgp):
    as_numbers = {}  # node -> AS number
    as_generator = iter(as_range)
    spine_as_numbers = {}  # spine -> AS number
    spine_pods = {}  # pod -> list of spines

    # Determine pod membership based on links
    for link in data['topology']['links']:
        node1, _ = link['endpoints'][0].split(':')
        node2, _ = link['endpoints'][1].split(':')

        if 'config' in data['topology']['nodes'][node1] and 'config' in data['topology']['nodes'][node2]:
            node1_type = data['topology']['nodes'][node1]['config']['vars']['type']
            node2_type = data['topology']['nodes'][node2]['config']['vars']['type']
        else:
            continue

        if node1_type == 'spine' and node2_type == 'leaf':
            # Assume that the spine and leaf are in the same pod
            if node1 not in spine_pods:
                spine_pods[node1] = []
            spine_pods[node1].append(node2)

        elif node2_type == 'spine' and node1_type == 'leaf':
            # Assume that the spine and leaf are in the same pod
            if node2 not in spine_pods:
                spine_pods[node2] = []
            spine_pods[node2].append(node1)

    # Assign AS numbers
    for node, config in data['topology']['nodes'].items():
        if 'config' not in data['topology']['nodes'][node]:
            continue
        node_type = config['config']['vars']['type']

        if node_type == 'leaf':
            as_numbers[node] = next(as_generator)
            # Add AS number to neighbor
            for neighbor in neighbors_bgp.values():
                if node in neighbor:
                    neighbor[node]['as'] = as_numbers[node]

        elif node_type == 'spine':
            # Get the pod of this spine (the first leaf it's connected to)
            pod = spine_pods[node][0]

            if pod not in spine_as_numbers:
                spine_as_numbers[pod] = next(as_generator)

            as_numbers[node] = spine_as_numbers[pod]
            # Add AS number to neighbor
            for neighbor in neighbors_bgp.values():
                if node in neighbor:
                    neighbor[node]['as'] = as_numbers[node]

        elif node_type == 'super-spine':
            # All super-spines share the same AS number
            if 'super-spine' not in spine_as_numbers:
                spine_as_numbers['super-spine'] = next(as_generator)

            as_numbers[node] = spine_as_numbers['super-spine']
            # Add AS number to neighbor
            for neighbor in neighbors_bgp.values():
                if node in neighbor:
                    neighbor[node]['as'] = as_numbers[node]

    return as_numbers, neighbors_bgp
