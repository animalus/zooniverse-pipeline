""" This version is written in Python 3.7"""
import argparse
import os
import io
from PIL import Image
import panoptes_client
from panoptes_client import SubjectSet, Subject, Project, Panoptes


def compress(original_location, original_file, resized_width):
    orig_image = Image.open(os.path.join(original_location, original_file))
    width, height = orig_image.size
    #  calculate the scale factor required and resized height
    scale = float(resized_width) / width
    scaled_size = (resized_width, int(height * scale))
    #  resize the image
    resized_file = orig_image.resize(scaled_size, Image.ANTIALIAS)
    #  save it in a file-like object (in memory) and find the size
    file_bytes = io.BytesIO()
    resized_file.save(file_bytes, optimize=True, quality=100, format='jpeg')
    size = file_bytes.tell()
    print('Uploading ', original_file, scale, resized_width, size)
    #  ensure the file pointer is returned to the beginning of the file-like object
    file_bytes.seek(0, 0)
    return file_bytes


parser = argparse.ArgumentParser(description='Zooniverse Uploader')
parser.add_argument('image_dir')
parser.add_argument('--subject', '-s', required=True)
args = parser.parse_args()

set_name = args.subject

#  connect to zooniverse - requires the User_name and Password to be set up as environmental variables in your OS
Panoptes.connect(username=os.environ['ZOONIVERSE_USERNAME'], password=os.environ['ZOONIVERSE_PASSWORD'])
#  modify the project slug if used for other than Snapshots at Sea
project = Project.find(slug='tedcheese/snapshots-at-sea')

if not os.path.exists(args.image_dir):
    print('[%s] does not exist.' % args.image_dir)
    sys.exit()

#  load the list of image files found in the directory:
#  The local file name will be uploaded as metadata with the image
file_types = ['jpg', 'jpeg']
subject_metadata = {}
for entry in os.listdir(args.image_dir):
    if entry.partition('.')[2].lower() in file_types:
        subject_metadata[entry] = {'Filename': entry}
print('Found ', len(subject_metadata), ' files to upload in this directory.')

previous_subjects = []

try:
    # check if the subject set already exits
    subject_set = SubjectSet.where(project_id=project.id, display_name=set_name).next()
    print('You have chosen to upload %d files to an existing subject set [%s]', % (len(subject_metadata), set_name))
    retry = input('Enter "n" to cancel this upload, any other key to continue' + '\n')
    if retry.lower() == 'n':
        quit()
    print('\n', 'It may take a while to recover the names of files previously uploaded, to ensure no duplicates')
    for subject in subject_set.subjects:
        previous_subjects.append(subject.metadata['Filename'])
except StopIteration:
    # create a new subject set for the new data and link it to the project above
    subject_set = SubjectSet()
    subject_set.links.project = project
    subject_set.display_name = set_name
    subject_set.save()

print('Uploading subjects, this could take a while!')
new_subjects = 0
for filename, metadata in subject_metadata.items():
    try:
        if filename not in previous_subjects:
            subject = Subject()
            subject.links.project = project
            subject.add_location(compress(args.image_dir, filename, 960))
            subject.metadata.update(metadata)
            subject.save()
            subject_set.add(subject.id)
            new_subjects += 1
    except panoptes_client.panoptes.PanoptesAPIException:
        print('An error occurred during the upload of ', filename)
print(new_subjects, 'new subjects created and uploaded')
print('Uploading complete, Please wait while the full subject listing is prepared and saved in')

output_file = "uploaded_subjects.csv"

print('"%s" in the drive with the original images' % output_file)

uploaded = 0
with open(os.path.join(args.image_dir, output_file), 'wt') as file_up:
    file_up.write('subject.id' + ',' + 'Filename' + '\n')
    subject_set = SubjectSet.where(project_id=project.id, display_name=set_name).next()
    for subject in subject_set.subjects:
        uploaded += 1
        file_up.write(subject.id + ',' + list(subject.metadata.values())[0] + '\n')
    print(uploaded, ' subjects found in the subject set, see the full list in %s.' % output_file)
