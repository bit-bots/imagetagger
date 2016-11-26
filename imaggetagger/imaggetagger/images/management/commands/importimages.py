from django.conf import settings
import os
import sys
from django.core.management.base import BaseCommand
from imaggetagger.images.models import ImageSet, Image


class Command(BaseCommand):

    # def add_arguments(self, parser):
    #    parser.add_argument('arg_imageset')

    def handle(self, *args, **options):
        url = settings.STATIC_ROOT + settings.IMAGE_PATH
    #    print(options['arg_imageset'])
        print('url: ', url)
        dirnames = [e for e in os.listdir(url) if os.path.isdir(url + e)]
        print(dirnames)
        imagesets = ImageSet.objects.all()
        for dir in dirnames:
            if not list(filter(lambda x: x.path == dir, imagesets)):
                if query_yes_no('Couldn\'t find an ImageSet for the directory "' + dir + '". Do you want to create a new one? ') == 'yes':
                    setname = input('How do you want to call your new imageset? ')
                    setlocation = input('What is the location your imageset got created? (Not the filepath) ')
                    ImageSet(path=dir, name=setname, location=setlocation).save()
                    setimages = []
                else:
                    continue
            else:
                setimages = Image.objects.filter(image_set=ImageSet.objects.get(path=dir))
                setimages = [x.name for x in setimages]
            print(setimages)

            filenames = [f for f in os.listdir(url + dir)]
            print(dir)
            for filename in filenames:
                (shortname, extension) = os.path.splitext(filename)
                if(extension.lower() in settings.IMAGE_EXTENSION and filename not in setimages):
                    Image(name = filename, image_set = ImageSet.objects.get(path=dir)).save()

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.
    
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":"yes",   "y":"yes",  "ye":"yes",
             "no":"no",     "n":"no"}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")
