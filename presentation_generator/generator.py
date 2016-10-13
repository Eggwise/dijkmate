import os
from presentation_generator.models import Folder



###  =============   FUNCTIONS     =============  ###

def extract_slides_from_config(config):
    slides = config['slides']
    order = config['order']

    extracted_slides = [slides[slide_name] for slide_name in order]
    return extracted_slides

def render_slides_at_folder(folder, template):
    config = folder.config.yaml
    slides = extract_slides_from_config(config)
    slides_string = '\n'.join([template.render(**slide) for slide in slides])
    return slides_string

def render_slides(content_root_folder, template):
    root_config = content_root_folder.config.yaml
    order = root_config['order']

    slides = []
    for slide_name in order:
        slide_folder = getattr(content_root_folder, slide_name)
        slides.append(render_slides_at_folder(slide_folder, template))

    return slides


###  =============   FUNCTIONS  END   =============  ###





def main():
    cur_dir = os.path.realpath(os.path.dirname(__file__))
    cur_folder = Folder(cur_dir)

    ###  =============   get main config    =============  ###
    main_config = cur_folder.config.yaml
    presentation_config = main_config['presentation']
    content_config = main_config['content']

    ###  =============   get content dir    =============  ###
    content_dirname = content_config['dirname']

    # check for content in current dir
    if cur_folder.has_dir(content_dirname):
        content_root_folder = cur_folder.get_folder(content_dirname)
        # check for content in upper dir
    elif cur_folder.parent.has_dir(content_dirname):
        content_root_folder = cur_folder.parent.get_folder(content_dirname)
    else:
        error = 'COULD NOT FIND CONTENT DIR IN CURRENT FOLDER OR PARENT FOLDER \n content dir name: {0}'.format(
            content_dirname)
        print(error)
        print('current folder: {0}'.format(cur_folder.path))
        print('parent folder: {0}'.format(cur_folder.parent.path))
        raise Exception(error)

    ###  =============   get templates    =============  ###
    templates = Folder(cur_dir).templates
    slide_template = templates.slide.template
    presentation_template = templates.presentation.template


    ###  =============   render slides    =============  ###
    slides = render_slides(content_root_folder, slide_template)


    ###  =============   render presentation    =============  ###
    rendered_presentation = presentation_template.render(slides=slides)
    pres_filename = presentation_config['filename']
    pres_title = presentation_config['title']


    dist_path = cur_folder.parent.dist.path


    with open(os.path.join(dist_path, pres_filename), 'w') as f:
        f.write(rendered_presentation)



main()