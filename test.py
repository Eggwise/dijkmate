url = 'http://cloud.funda.nl/valentina_media/065/252/533_1440x960.jpg'

import yaml, os, jinja2


from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('dijkmate', 'templates'))


test = env.get_template('slide.template.html')