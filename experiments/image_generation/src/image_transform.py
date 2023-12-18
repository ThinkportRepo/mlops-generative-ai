import json

import numpy as np
from matplotlib import pyplot as plt


def display_img_and_prompt(img, prmpt):
    """Display hallucinated image."""
    plt.figure(figsize=(12, 12))
    x = np.array(img)
    print(x.shape)
    plt.imshow(np.array(img))
    plt.axis("off")
    plt.title(prmpt)
    plt.show()


if __name__ == "__main__":
    # Opening JSON file
    f = open('cedar_apple_rust.json')

    # returns JSON object as
    # a dictionary
    data = json.load(f)

    # Iterating through the json
    # list
    for element in data:
        display_img_and_prompt(element['generated_image'], element['prompt'])

    # Closing file
    f.close()