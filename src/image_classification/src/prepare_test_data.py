"""
Script to move a few images from the original dataset
into the test dataset folder randomly.
"""

import shutil
import glob
import random
import os

from src.image_classification.src.training.class_names import class_names as CLASS_NAMES

random.seed(42)

ROOT_DIR = os.path.join('..', 'input', 'plantvillage dataset', 'color')
DEST_DIR = os.path.join('..', 'input', 'test')
# Class directories.
class_dirs = CLASS_NAMES
# Test images.
test_image_num = 100

for class_dir in class_dirs:
    os.makedirs(os.path.join(DEST_DIR, class_dir), exist_ok=True)
    init_image_paths = glob.glob(os.path.join(ROOT_DIR, class_dir, '*'))
    print(f"Initial number of images for class {class_dir}: {len(init_image_paths)}")
    random.shuffle(init_image_paths)
    for i in range(test_image_num):
        image_name = init_image_paths[i].split(os.path.sep)[-1]
        shutil.move(
            init_image_paths[i], 
            os.path.join(DEST_DIR, class_dir, image_name)
        )
    final_image_paths = glob.glob(os.path.join(ROOT_DIR, class_dir, '*'))
    print(f"Final number of images for class {class_dir}: {len(final_image_paths)}\n")