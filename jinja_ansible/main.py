import yaml
from jinja2 import Template
import os

# Create the "playbooks" folder if it doesn't exist
os.makedirs('playbooks', exist_ok=True)

# Load the Jinja template from a file
with open('templates/interfaces.j2', 'r') as template_file:
    template = Template(template_file.read())

# Read the data from the input YAML file
with open('input.yml', 'r') as yaml_file:
    data = yaml.safe_load(yaml_file)
    nodes = data['topology']['nodes']

# Iterate over each node and generate a playbook
for node, config in nodes.items():
    if 'config' in config and 'vars' in config['config']:
        # Prepare the necessary inputs for the Jinja template
        interface = {
            'node': node,
            'interface-name': config['config']['vars'].get('interface-name', ''),
            'ip-address-p2p': config['config']['vars'].get('ip-address-p2p', ''),
            'ip-address-loopback': config['config']['vars'].get('ip-address-loopback', '')
        }

        # Render the template with the necessary inputs
        rendered_playbook = template.render(interfaces=[interface])

        # Write the rendered playbook to a file
        playbook_filename = f"playbooks/generated_playbook_{node}.yml"
        with open(playbook_filename, 'w') as playbook_file:
            playbook_file.write(rendered_playbook)

        print(f"Generated playbook for {node}: {playbook_filename}")




#Basic test for simple template example
""" from jinja2 import Template

# Load the Jinja template from a file
with open('template.j2', 'r') as template_file:
    template = Template(template_file.read())

# Define the variable values
variables = {
    'location': 'Some location',
    'contact': 'Some contact'
}

# Render the template with the variable values
rendered_playbook = template.render(variables)

# Write the rendered playbook to a file
with open('generated_playbook.yml', 'w') as playbook_file:
    playbook_file.write(rendered_playbook)
"""