def generate_as_numbers(data, as_range, neighbors):
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
            for neighbor in neighbors.values():
                if node in neighbor:
                    neighbor[node]['as'] = as_numbers[node]

        elif node_type == 'spine':
            # Get the pod of this spine (the first leaf it's connected to)
            pod = spine_pods[node][0]

            if pod not in spine_as_numbers:
                spine_as_numbers[pod] = next(as_generator)

            as_numbers[node] = spine_as_numbers[pod]
            # Add AS number to neighbor
            for neighbor in neighbors.values():
                if node in neighbor:
                    neighbor[node]['as'] = as_numbers[node]

        elif node_type == 'super-spine':
            # All super-spines share the same AS number
            if 'super-spine' not in spine_as_numbers:
                spine_as_numbers['super-spine'] = next(as_generator)

            as_numbers[node] = spine_as_numbers['super-spine']
            # Add AS number to neighbor
            for neighbor in neighbors.values():
                if node in neighbor:
                    neighbor[node]['as'] = as_numbers[node]

    return as_numbers, neighbors

# 2ND ATTEMPT
""" def generate_as_numbers(data, leaf_as_range, spine_as_range, super_spine_as_range):
    as_numbers = {}  # node -> as_number
    leaf_as = iter(leaf_as_range)
    spine_as = iter(spine_as_range)
    super_spine_as = iter(super_spine_as_range)

    for node, config in data['topology']['nodes'].items():
        # Assign AS numbers based on node type
        node_type = config['config']['vars']['type']
        if node_type == 'leaf':
            try:
                as_numbers[node] = next(leaf_as)
            except StopIteration:
                raise ValueError(f'Ran out of AS numbers for leaf switches at {node}')
        elif node_type == 'spine':
            try:
                as_numbers[node] = next(spine_as)
            except StopIteration:
                raise ValueError(f'Ran out of AS numbers for spine switches at {node}')
        elif node_type == 'super-spine':
            try:
                as_numbers[node] = next(super_spine_as)
            except StopIteration:
                raise ValueError(f'Ran out of AS numbers for super-spine switches at {node}')
        else:
            raise ValueError(f'Type not recognized at {node}, should be leaf, spine or super-spine')
        
    return as_numbers

# HOW IT SHOULD BE CALLED
as_numbers = generate_as_numbers(
    data,
    leaf_as_range=range(64512, 65500),
    spine_as_range=range(65500, 65510),
    super_spine_as_range=range(65510, 65520)
) """

# DEFAULT 1ST ATTEMPT
""" def generate_as_numbers(data):
    as_number_start = 64512
    as_numbers = {}  # node -> as_number
    spine_as = 65500  # fixed AS number for all spine switches in a pod
    leaf_as = 65501  # incrementing AS number for all leaf switches
    super_spine_as = 65535  # fixed AS number for all super-spine switches

    for node, config in data['topology']['nodes'].items():
        # Assign AS numbers based on node type
        node_type = config['config']['vars']['type']
        if node_type == 'leaf':
            as_numbers[node] = leaf_as
            leaf_as += 1
        elif node_type == 'spine':
            as_numbers[node] = spine_as
        elif node_type == 'super-spine':
            as_numbers[node] = super_spine_as
        # Assign same AS number to all other types of nodes
        else:
            return "Error: Type of node not defined."

    return as_numbers """