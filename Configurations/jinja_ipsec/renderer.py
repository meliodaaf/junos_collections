from jinja2 import Template
import yaml

# Load the YAML data
with open('ipsec_yml.yml') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)

# Render the Jinja template
with open('ipsec_template.j2') as file:
    template = Template(file.read())
    rendered_config = template.render(phase1=data["phase1"])

print(rendered_config)