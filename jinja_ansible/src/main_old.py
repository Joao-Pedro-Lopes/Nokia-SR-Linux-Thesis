import os
import sys
import yaml
from jinja2 import Template
from config_template import config_template

# Create the "playbooks" folder if it doesn't exist
os.makedirs('playbooks', exist_ok=True)

# To know which configuration should be generated
# interfaces
# ebgp
# ibgp
config_type = sys.argv[-1]

# Load the Jinja template from a file
with open(f'../templates/{config_type}.j2', 'r') as template_file:
    template = Template(template_file.read())

# Read the data from the input YAML file
with open('../input.yml', 'r') as yaml_file:
    data = yaml.safe_load(yaml_file)
    nodes = data['topology']['nodes']

# Iterate over each node and generate a playbook
for node, config in nodes.items():
    if 'config' in config and 'vars' in config['config']:
        # Prepare the necessary inputs for the Jinja template
        variables = config_template(config_type, node, config)
        if (variables is None): 
            print('Invalid configuration type.')
            sys.exit()

        # Render the template with the necessary inputs
        rendered_playbook = template.render(config_type=[variables])

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