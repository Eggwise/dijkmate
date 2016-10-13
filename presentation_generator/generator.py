import os
from presentation_generator.models import Folder
import shutil

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


images_folder = content_root_folder.images

dist_folder = cur_folder.parent.dist

###  =============   get templates    =============  ###
templates = Folder(cur_dir).templates
slide_template = templates.slide.template
presentation_template = templates.presentation.template



###  =============   FUNCTIONS     =============  ###

def extract_slides_from_config(config):
    slides = config['slides']
    order = config['order']

    extracted_slides = [{'name': slide_name, **slides[slide_name]} for slide_name in order]
    return extracted_slides

def render_slides_at_folder(folder, template):
    config = folder.config.yaml
    slides = extract_slides_from_config(config)
    slides_string = '\n'.join([template.render(**slide) for slide in slides])
    return slides_string




def render_slides(content_root_folder):
    root_config = content_root_folder.config.yaml
    order = root_config['order']

    slides = []
    slide_configs = []
    for slide_name in order:
        slide_folder = getattr(content_root_folder, slide_name)
        slide_folder_config = slide_folder.config.yaml
        slides = extract_slides_from_config(slide_folder_config)
        slide_configs.append(slides)

    #validate slides
    for slides in slide_configs:
        for slide in slides:
            if 'background' in slide and slide['background'] is not None and len(slide['background'].strip()) != 0:
                slide_background = slide['background']
                if not images_folder.has_file(slide_background):
                    error = 'could not find image: {0} at slide {1}'.format(slide_background, slide['name'])
                    print('ERROR: {0}'.format(error))
                    raise Exception(error)

            #check image
            slide_text = slide['text'] or None

    output_image_path = os.path.join(dist_folder.path, 'images')
    #delete all images
    if os.path.exists(output_image_path):
        shutil.rmtree(dist_folder.images.path)

    os.mkdir(output_image_path)


    #move images and render slides
    all_rendered_slides = []
    for slides in slide_configs:
        rendered_slides = []
        for slide in slides:

            if 'background' in slide and slide['background'] is not None and len(slide['background'].strip()) != 0:
                slide_background = slide['background']
                #copy image to dist
                image_path = images_folder.get_file(slide_background).path
                shutil.copy(image_path, output_image_path)

            #delete unfilled attributes
            empty_attribute_keys = [k for k, v in slide.items() if v is None or len(v) == 0]
            for i in empty_attribute_keys:

                del(slide[i])

            rendered_slide = slide_template.render(**slide)
            rendered_slides.append(rendered_slide)

        all_rendered_slides.append('\n'.join(rendered_slides))


    return all_rendered_slides



###  =============   FUNCTIONS  END   =============  ###







def main():




    ###  =============   render slides    =============  ###
    slides = render_slides(content_root_folder)


    ###  =============   render presentation    =============  ###
    rendered_presentation = presentation_template.render(slides=slides)
    pres_filename = presentation_config['filename']
    pres_title = presentation_config['title']


    dist_path = cur_folder.parent.dist.path


    with open(os.path.join(dist_path, pres_filename), 'w') as f:
        f.write(rendered_presentation)



main()