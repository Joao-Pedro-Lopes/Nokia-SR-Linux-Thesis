import os
import sys
import yaml
from jinja2 import Template
from config_template import config_interfaces, config_ebgp, config_ibgp, config_mac_vrf
from generate_ip_addresses import generate_ip_addresses
from generate_as_numbers import generate_as_numbers
from generate_inventory import generate_inventory

# To know which configuration should be generated -- interfaces / ebgp / ibgp / mac-vrf / general
config_type = sys.argv[-1]

# Load the Jinja template from a file
with open(f'../templates/{config_type}.j2', 'r') as template_file:
    template = Template(template_file.read())

# Read the data from the input YAML file
with open('../inputs/input.yml', 'r') as yaml_file:
    data = yaml.safe_load(yaml_file)
    nodes = data['topology']['nodes']

# Create the "playbooks" folder if it doesn't exist
playbooks_directory = f'../playbooks/'
#playbooks_directory = f'../playbooks/clab-{data["name"]}'
os.makedirs(playbooks_directory, exist_ok=True)

# Initialize inventory file content
inventory_content = ['[clab]']

# Generate IP addresses
interface_ips, interface_mac_vrf, loopback_ips, neighbors_bgp, neighbors_ibgp = generate_ip_addresses(data)

# Generate and attribute AS numbers for eBGP
as_number_min = int(data['topology']['defaults']['env']['AS_NUMBER_EBGP_RANGE'].split("-")[0])
as_number_max = int(data['topology']['defaults']['env']['AS_NUMBER_EBGP_RANGE'].split("-")[1])
as_numbers, neighbors_bgp = generate_as_numbers(data, range(as_number_min, as_number_max), neighbors_bgp)

vxlan_name = data['topology']['defaults']['env']['VXLAN_NAME']
vxlan_interface = data['topology']['defaults']['env']['VXLAN_INTERFACE']
vni = int(data['topology']['defaults']['env']['VNI'])
vrf_name = data['topology']['defaults']['env']['VRF_NAME']

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
            variables = config_mac_vrf(node, interface_mac_vrf)
            # Render the template with the necessary inputs
            rendered_playbook = template.render(host_name=host_name, interface=variables['interface'], node=node, vxlan_name=vxlan_name, vxlan_interface=vxlan_interface, vni=vni, vrf_name=vrf_name)
        if config_type == 'general':
            variables_interfaces = config_interfaces(node, interface_ips)
            variables_ebgp = config_ebgp(node, as_numbers, loopback_ips, neighbors_bgp[node])
            variables_ibgp = config_ibgp(node, as_numbers, loopback_ips, neighbors_ibgp[node], data['topology']['defaults']['env']['AS_NUMBER_IBGP_VALUE'])
            is_route_reflector = data['topology']['nodes'][node]['config']['vars'].get('is_route_reflector', False)
            
            # Render the template with the necessary inputs
            if node not in interface_mac_vrf:
                rendered_playbook = template.render(host_name=host_name, node=node, interfaces=variables_interfaces['interfaces'], ip_address_loopback=loopback_ips[node], ebgp=variables_ebgp['ebgp'], ibgp=variables_ibgp['ibgp'], neighbors_ebgp=variables_ebgp['peers'], neighbors_ibgp=variables_ibgp['peers'], route_reflector=is_route_reflector, needs_mac_vrf=False)
            else:
                variables_mac_vrf = config_mac_vrf(node, interface_mac_vrf)
                rendered_playbook = template.render(host_name=host_name, node=node, interfaces=variables_interfaces['interfaces'], ip_address_loopback=loopback_ips[node], ebgp=variables_ebgp['ebgp'], ibgp=variables_ibgp['ibgp'], neighbors_ebgp=variables_ebgp['peers'], neighbors_ibgp=variables_ibgp['peers'], interface_mac_vrf=variables_mac_vrf['interface'], vxlan_name=vxlan_name, vxlan_interface=vxlan_interface, vni=vni, vrf_name=vrf_name, route_reflector=is_route_reflector, needs_mac_vrf=True)

            #rendered_playbook = template.render(host_name=host_name, node=node, interfaces=variables_interfaces['interfaces'], ip_address_loopback=loopback_ips[node], ebgp=variables_ebgp['ebgp'], ibgp=variables_ibgp['ibgp'], neighbors_ebgp=variables_ebgp['peers'], neighbors_ibgp=variables_ibgp['peers'], route_reflector=is_route_reflector)
            #rendered_playbook = template.render(host_name=host_name, node=node, interfaces=variables_interfaces['interfaces'], ip_address_loopback=loopback_ips[node], ebgp=variables_ebgp['ebgp'], ibgp=variables_ibgp['ibgp'], neighbors_ebgp=variables_ebgp['peers'], neighbors_ibgp=variables_ibgp['peers'], interface_mac_vrf=variables_mac_vrf['interface'], vxlan_name=vxlan_name, vxlan_interface=vxlan_interface, vni=vni, vrf_name=vrf_name)

        # Write the rendered playbook to a file
        playbook_filename = f'{playbooks_directory}/{config_type}_{node}_generated_playbook.yml'
        with open(playbook_filename, 'w') as playbook_file:
            playbook_file.write(rendered_playbook)
        
        print(f'Generated playbook for {node}: {playbook_filename}')
    
# Write the inventory content to a file

# Join the list of lines into a single string with newline characters between each line
inventory_content_str = '\n'.join(inventory_content)

inventory_filepath = f'{playbooks_directory}/inventory.yml'
with open(inventory_filepath, 'w') as inventory_file:
    inventory_file.write(inventory_content_str)

print(f'Generated inventory file: {inventory_filepath}')

