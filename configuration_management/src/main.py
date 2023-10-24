import os
import sys
import yaml
import json
from jinja2 import Template
from config_template import config_interfaces, config_ebgp, config_ibgp, config_mac_vrf
from generate_ip_addresses import generate_ip_addresses
from generate_as_numbers import generate_as_numbers
from generate_inventory import generate_inventory
from util import transform_dict

# To know which configuration file must be loaded
input_file = sys.argv[-2]
# To know which configuration should be generated -- interfaces / ebgp / ibgp / mac-vrf / general
config_type = sys.argv[-1]

# Load the Jinja template from a file
with open(f'../templates/{config_type}.j2', 'r') as template_file:
    template = Template(template_file.read())

with open(f'../templates/gnmic-config.j2', 'r') as template_file:
    gnmic_config_template = Template(template_file.read())

with open(f'../templates/alert_rules.j2', 'r') as template_file:
    alert_rules_template = Template(template_file.read())

# Read the data from the input YAML file
with open(input_file, 'r') as yaml_file:
    data = yaml.safe_load(yaml_file)
    nodes = data['topology']['nodes']

# Create the "playbooks" folder if it doesn't exist
playbooks_directory = f'../playbooks'
os.makedirs(playbooks_directory, exist_ok=True)

# Initialize inventory file content
inventory_content = ['[clab]']

# Generate IP addresses
interface_ips, interface_mac_vrf, loopback_ips, neighbors_bgp, neighbors_ibgp = generate_ip_addresses(data)
print(interface_ips)

# Generate and attribute AS numbers for eBGP
as_number_min = int(data['topology']['defaults']['env']['AS_NUMBER_EBGP_RANGE'].split("-")[0])
as_number_max = int(data['topology']['defaults']['env']['AS_NUMBER_EBGP_RANGE'].split("-")[1])
as_numbers, neighbors_bgp = generate_as_numbers(data, range(as_number_min, as_number_max), neighbors_bgp)

vrfs = {}
for key, value in data["topology"]["defaults"]["env"].items():
    if key.startswith("VRF"):
        try:
            vrf_info = json.loads(value) # value would be the dictionary corresponding to each VRF
        except json.JSONDecodeError:
            print(f"Warning: Failed to decode {value} as JSON, skipping.")
            continue

        vrfs[vrf_info['id']] = {}
        vrfs[vrf_info['id']]['id'] = vrf_info['id']  # vxlan_interface and vni can be equal to this
        vrfs[vrf_info['id']]['vlan_id'] = vrf_info['VLAN_ID']
        vrfs[vrf_info['id']]['vxlan_name'] = vrf_info['VXLAN_NAME']
        vrfs[vrf_info['id']]['vrf_name'] = vrf_info['VRF_NAME']

# Iterate over each node and generate a playbook
for node, config in nodes.items():
    if 'config' in config and 'vars' in config['config']:
        # Prepare the necessary inputs for the Jinja template

        # Construct the host_name variable
        host_name = f'clab-{data["name"]}-{node}'
        inventory_content = generate_inventory(inventory_content, host_name)

        if config_type == 'interfaces':
            variables = config_interfaces(node, interface_ips)
            # Render the template with the necessary inputs
            rendered_playbook = template.render(host_name=host_name, interfaces=variables['interfaces'], node=node, ip_address_loopback=loopback_ips[node])
        if config_type == 'ebgp':
            variables = config_ebgp(node, as_numbers, loopback_ips, neighbors_bgp[node])
            # Render the template with the necessary inputs
            rendered_playbook = template.render(host_name=host_name, node=node, ebgp=variables['ebgp'], neighbors=variables['peers'])
        if config_type == 'ibgp':
            variables = config_ibgp(node, as_numbers, loopback_ips, neighbors_ibgp[node], data['topology']['defaults']['env']['AS_NUMBER_IBGP_VALUE'])
            is_route_reflector = data['topology']['nodes'][node]['config']['vars'].get('is_route_reflector', False)
            # Render the template with the necessary inputs
            rendered_playbook = template.render(host_name=host_name, node=node, ibgp=variables['ibgp'], neighbors=variables['peers'], route_reflector=is_route_reflector)
        if config_type == 'mac-vrf':
            if node not in interface_mac_vrf:
                continue
            variables = config_mac_vrf(node, interface_mac_vrf, vrfs)
            # Render the template with the necessary inputs
            rendered_playbook = template.render(host_name=host_name, interfaces=variables['interfaces'], node=node)
        if config_type == 'general':
            variables_interfaces = config_interfaces(node, interface_ips)
            variables_ebgp = config_ebgp(node, as_numbers, loopback_ips, neighbors_bgp[node])

            needs_ibgp = False
            if node in neighbors_ibgp:
                variables_ibgp = config_ibgp(node, as_numbers, loopback_ips, neighbors_ibgp[node], data['topology']['defaults']['env']['AS_NUMBER_IBGP_VALUE'])
                needs_ibgp = True
            
            is_route_reflector = data['topology']['nodes'][node]['config']['vars'].get('is_route_reflector', False)

            # Render the template with the necessary inputs
            if node not in interface_mac_vrf:
                rendered_playbook = template.render(host_name=host_name, node=node, interfaces=variables_interfaces['interfaces'], ip_address_loopback=loopback_ips[node], ebgp=variables_ebgp['ebgp'], needs_ibgp=needs_ibgp, ibgp=variables_ibgp['ibgp'], neighbors_ebgp=variables_ebgp['peers'], neighbors_ibgp=variables_ibgp['peers'], route_reflector=is_route_reflector, needs_mac_vrf=False)
            else:
                variables_mac_vrf = config_mac_vrf(node, interface_mac_vrf, vrfs)
                rendered_playbook = template.render(host_name=host_name, node=node, interfaces=variables_interfaces['interfaces'], ip_address_loopback=loopback_ips[node], ebgp=variables_ebgp['ebgp'], needs_ibgp=needs_ibgp, ibgp=variables_ibgp['ibgp'], neighbors_ebgp=variables_ebgp['peers'], neighbors_ibgp=variables_ibgp['peers'], route_reflector=is_route_reflector, needs_mac_vrf=True, interfaces_mac_vrf=variables_mac_vrf['interfaces'])

        # Write the rendered playbook to a file
        playbook_filename = f'{playbooks_directory}/{config_type}_{node}_generated_playbook.yml'
        with open(playbook_filename, 'w') as playbook_file:
            playbook_file.write(rendered_playbook)
        
        print(f'Generated playbook for {node}: {playbook_filename}')
    
# Write the inventory content to a file
inventory_content_str = '\n'.join(inventory_content) # Join the list of lines into a single string with newline characters between each line

inventory_filepath = f'{playbooks_directory}/inventory.yml'
with open(inventory_filepath, 'w') as inventory_file:
    inventory_file.write(inventory_content_str)

print(f'Generated inventory file: {inventory_filepath}')

nodes = transform_dict(interface_ips)
# Write targets to gnmic config file
with open("../../visualization_monitoring/gnmic-config.yml", "w") as f:
    f.write(gnmic_config_template.render(nodes=nodes))

# Write alert rules
with open("../../visualization_monitoring/configs/prometheus/alert_rules.yml", "w") as f:
    f.write(alert_rules_template.render(nodes=nodes))