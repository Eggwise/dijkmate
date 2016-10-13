import os, json, jinja2
from models import SourceFile, Folder
import logging
cur_dir = os.path.realpath(os.curdir)

content_dir = os.path.join(cur_dir, 'content')
logging.basicConfig(level=1)
test = Folder(content_dir)


print(test)

