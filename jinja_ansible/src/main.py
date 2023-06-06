import os
import sys
import yaml
from jinja2 import Template
from config_template import config_interfaces, config_ebgp, config_ibgp
from generate_ip_addresses import generate_ip_addresses
from generate_as_numbers import generate_as_numbers

# Create the "playbooks" folder if it doesn't exist
os.makedirs('../playbooks', exist_ok=True)

# To know which configuration should be generated -- interfaces / ebgp / ibgp
config_type = sys.argv[-1]

# Load the Jinja template from a file
with open(f'../templates/{config_type}.j2', 'r') as template_file:
    template = Template(template_file.read())

# Read the data from the input YAML file
with open('../inputs/input.yml', 'r') as yaml_file:
    data = yaml.safe_load(yaml_file)
    nodes = data['topology']['nodes']

print(data['topology']['defaults']['env'])

# Generate IP addresses
interface_ips, loopback_ips, neighbors_bgp, neighbors_ibgp = generate_ip_addresses(data)

print(neighbors_bgp)

as_number_min = int(data['topology']['defaults']['env']['AS_NUMBER_EBGP_RANGE'].split("-")[0])
as_number_max = int(data['topology']['defaults']['env']['AS_NUMBER_EBGP_RANGE'].split("-")[1])
# Generate and attribute AS numbers for eBGP
as_numbers, neighbors_bgp = generate_as_numbers(data, range(as_number_min, as_number_max), neighbors_bgp)

# Iterate over each node and generate a playbook
for node, config in nodes.items():
    if 'config' in config and 'vars' in config['config']:
        # Prepare the necessary inputs for the Jinja template

        # Construct the host_name variable
        host_name = f'clab-{data["name"]}-{node}'

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
            # Render the template with the necessary inputs
            rendered_playbook = template.render(host_name=host_name, node=node, ibgp=variables['ibgp'], neighbors=variables['peers'])
        if config_type == 'general':
            variables_interfaces = config_interfaces(node, interface_ips)
            variables_ebgp = config_ebgp(node, as_numbers, loopback_ips, neighbors_bgp[node])
            variables_ibgp = config_ibgp(node, as_numbers, loopback_ips, neighbors_ibgp[node], data['topology']['defaults']['env']['AS_NUMBER_IBGP_VALUE'])
            # Render the template with the necessary inputs
            rendered_playbook = template.render(host_name=host_name, node=node, interfaces=variables_interfaces['interfaces'], ip_address_loopback=loopback_ips[node], ebgp=variables_ebgp['ebgp'], ibgp=variables_ibgp['ibgp'], neighbors_ebgp=variables_ebgp['peers'], neighbors_ibgp=variables_ibgp['peers'])
        #FIXME: ibgp neighbor detection
        # Write the rendered playbook to a file
        playbook_filename = f"../playbooks/{config_type}_{node}_generated_playbook.yml"
        with open(playbook_filename, 'w') as playbook_file:
            playbook_file.write(rendered_playbook)

        print(f"Generated playbook for {node}: {playbook_filename}")

""" - name: Create configuration files
      ansible.builtin.command: |
        python3 src/main.py ../topology_template_v5.yml """
