from __future__ import print_function

import sys
import os
import shutil
import operator


import numpy as np
import scipy.io
import sklearn.cross_validation

from context import settings

root = os.path.join(settings.DATA_ROOT, 'car_type')
images = os.path.join(settings.DATA_ROOT, 'image')
labels = os.path.join(settings.DATA_ROOT, 'label')
attributes = os.path.join(settings.DATA_ROOT, 'misc/attributes.txt')


no_models = 0
image_count = 0

labels_dict = {}
imagefiles = []
labels = []

makes = os.listdir(images)
for make in makes:
  image_make = os.path.join(images, make)
  models = os.listdir(image_make)
  for model in models:
    image_make_model = os.path.join(image_make, model)
    no_images = 0
    for _, _, files in os.walk(image_make_model):
      no_images += len(files)
    if no_images < 100:
      continue # Ignore this model
    # Add this model to labels dict 
    labels_dict[model] = no_models
    no_models+=1
    years = os.listdir(image_make_model)
    for year in years:
      image_make_model_year = os.path.join(image_make_model, year)
      image_files = os.listdir(image_make_model_year)
      for image in image_files:
        imagefiles.append((os.path.join(image_make_model_year, image)))
        labels.append(labels_dict[model])
        image_count+=1

imagefiles = np.array(imagefiles, dtype=np.object)
labels = np.array(labels, dtype=np.int32)

# Perform Train/Valid/Test Split using Stratified Split
sss = sklearn.cross_validation.StratifiedShuffleSplit(labels, 1, 0.2)
for train_index, test_index in sss:
    imagefiles_train = imagefiles[train_index]
    labels_train = labels[train_index]
    imagefiles_test = imagefiles[test_index]
    labels_test = labels[test_index]
# Further spltting test into test and validation sets
sss = sklearn.cross_validation.StratifiedShuffleSplit(labels_test, 1, 0.5)
for valid_index, test_index in sss:
    imagefiles_valid = imagefiles_test[valid_index]
    labels_valid = labels_test[valid_index]
    imagefiles_test = imagefiles_test[test_index]
    labels_test = labels_test[test_index]

# The total number of samples should be in multiple of 10s
# to avoid nasty queuing errors/warnings later
N = (len(imagefiles_train)/10)*10
imagefiles_train = imagefiles_train[:N]
labels_train = labels_train[:N]
N = (len(imagefiles_valid)/10)*10
imagefiles_valid = imagefiles_valid[:N]
labels_valid = labels_valid[:N]
N = (len(imagefiles_test)/10)*10
imagefiles_test = imagefiles_test[:N]
labels_test = labels_test[:N]

# Writing Meta File for Training Data
f = open(settings.TRAIN_META, 'w')
for idx in range(len(imagefiles_train)):
  f.write('%s %d\n' % (imagefiles_train[idx], labels_train[idx]))

# Writing Meta File for Valid Data
f = open(settings.VALID_META, 'w')
for idx in range(len(imagefiles_valid)):
  f.write('%s %d\n' % (imagefiles_valid[idx], labels_valid[idx]))

# Writing Meta File for Test Data
f = open(settings.TEST_META, 'w')
for idx in range(len(imagefiles_test)):
  f.write('%s %d\n' % (imagefiles_test[idx], labels_test[idx]))

print ('#Models: %d' % no_models) 
print ('#TotalImages: %d %d %d' % (image_count, len(imagefiles), len(labels)))
print ('#TrainImages: %d' % len(imagefiles_train))
print ('#ValidImages: %d' % len(imagefiles_valid))
print ('#TestImages: %d' % len(imagefiles_test)) 