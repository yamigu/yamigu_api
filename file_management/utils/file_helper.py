from django.conf import settings
import uuid
import os
from PIL import Image, ExifTags


def save_uploaded_file(f, TAG):
    ext = f.name.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    root_path = os.path.join(settings.MEDIA_ROOT, TAG)
    file_path = os.path.join(root_path, filename)

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return filename


def get_file_path(filename, TAG):
    root_path = os.path.join(settings.MEDIA_ROOT, TAG)
    file_path = os.path.join(root_path, filename)
    return file_path


def rotate_image(filepath):
    try:
        image = Image.open(filepath)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)
        image.save(filepath)
        image.close()
    except (AttributeError, KeyError, IndexError):
        pass
