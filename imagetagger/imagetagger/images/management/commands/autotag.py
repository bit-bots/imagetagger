import os
import sys
import numpy as np
import cv2
import json
from imagetagger.images.models import ImageSet, Image, Annotation, AnnotationType
from keras.models import model_from_json
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(settings.DATA_PATH + "model.json", "r") as j:
            model = model_from_json(j.read())
        model.load_weights(settings.DATA_PATH + "model.ker")
        print('Enter image set name.')
        image_set_name = input()
        try:
            image_set_path = settings.IMAGE_PATH + ImageSet.objects.get(name=image_set_name).get_path()
        except ImageSet.model.DoesNotExist:
            print('Imageset not found.')
            sys.exit(1)
        print(image_set_path)
        ibx = 0
        listdir = list(os.listdir(image_set_path))
        for im in sorted(listdir):
            if not im.lower().endswith(tuple(settings.IMAGE_EXTENSION)):
                continue

            print(im)
            ra = cv2.imread(os.path.join(image_set_path, im))
            img = cv2.GaussianBlur(ra, (9, 9), 0)
            b, g, r = cv2.split(img)
            circles = cv2.HoughCircles(g, cv2.HOUGH_GRADIENT, 1, 100,
                                       param1=50, param2=43, minRadius=15, maxRadius=200)

            if circles is not None:
                circles = np.uint16(np.around(circles))
                try:
                    for i in circles[0, :]:
                        i[2] += 3
                        corp = ra[i[1] - i[2] - 3:i[1] + i[2] + 3, i[0] - i[2] - 3:i[0] + i[2] + 3]
                        # cv2.imshow("corp", corp)

                        corp = cv2.resize(corp, (30, 30), interpolation=cv2.INTER_CUBIC)
                        corp.reshape((1,) + corp.shape)
                        p = model.predict(np.array([corp]), verbose=0)

                        if p[0][0] >= 0.5:
                            try:
                                image = Image.objects.get(name=im)
                                print(i[0])
                                print(i[1])
                                print(i[2])
                                print()
                                vector = json.dumps({'x1': int(i[0] - i[2]), 'y1': int(i[1] - i[2]), 'x2': int(i[0] + i[2]), 'y2': int(i[1] + i[2])})
                                Annotation(image=image, vector=vector, type=AnnotationType.objects.get(name='ball')).save()
                            except (Image.DoesNotExist, AnnotationType.DoesNotExist) as e:
                                print('Image ' + im + ' not found.')
                        ibx += 1
                except cv2.error:
                    continue
