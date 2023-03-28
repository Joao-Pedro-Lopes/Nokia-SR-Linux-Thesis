""" import yaml

# load the YAML file containing the network topology information
with open("super_spine.yml", "r") as f:
    data = yaml.safe_load(f)

# create a dictionary to keep track of the type of each node
node_types = {}

# iterate over the nodes in the topology
for node in data['topology']["nodes"]:
    # initialize the type of each node to "unknown"
    node_types[node] = "unknown"

# iterate over the links in the topology
for link in data['topology']["links"]:
    # extract the source and target nodes from the link endpoints
    source_node, source_port = link["endpoints"][0].split(":")
    target_node, target_port = link["endpoints"][1].split(":")
    
    # determine the type of the target node based on the number and type of its links
    if node_types[target_node] == "unknown":
        if "e1-" in target_port:
            # the target node is a leaf switch
            node_types[target_node] = "leaf"
        else:
            # the target node is a spine switch
            spine_connections = sum(1 for l in data["links"] if l["endpoints"][1].startswith(target_node+":"))
            if spine_connections > 1:
                # the target node is a super spine switch
                node_types[target_node] = "super_spine"
            else:
                # the target node is a regular spine switch
                node_types[target_node] = "spine"

# print the type of each node
for node, node_type in node_types.items():
    print(node, node_type)
 """

import yaml

# load the topology file
with open("super_spine.yml", "r") as f:
    topology = yaml.safe_load(f)

# initialize dictionaries to store the connections of each node
node_connections = {}
for node in topology["topology"]["nodes"].keys():
    node_connections[node] = 0

# count the number of connections for each node
for link in topology["topology"]["links"]:
    endpoints = link["endpoints"]
    for endpoint in endpoints:
        node, iface = endpoint.split(":")
        node_connections[node] += 1

# determine if each node is a leaf, spine or super spine
leaf_nodes = []
spine_nodes = []
superspine_nodes = []
for node, connections in node_connections.items():
    if connections == 1:
        leaf_nodes.append(node)
    elif connections == 2:
        spine_nodes.append(node)
    elif connections == 3:
        superspine_nodes.append(node)

print("Leaf Nodes:", leaf_nodes)
print("Spine Nodes:", spine_nodes)
print("Super Spine Nodes:", superspine_nodes)