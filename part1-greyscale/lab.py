#!/usr/bin/env python3

import sys
import math
import base64
import tkinter

from io import BytesIO
from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, x, y):
    loc = x * image['width'] + y
    return image['pixels'][loc]


def set_pixel(image, x, y, c):
    loc = x * image['width'] + y
    image['pixels'][loc] = c


def apply_per_pixel(image, func):
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:],
    }
    for x in range(image['height']):
        for y in range(image['width']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
            #print("CURRENT RESULT", result)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)


# HELPER FUNCTIONS
def get_pixel_edge(image, x, y):
    if x < 0: x = 0
    elif x >= image['height']: x = image['height'] - 1
    if y < 0: y = 0
    elif y >= image['width']: y = image['width'] - 1
    loc = x * image['width'] + y
    return image['pixels'][loc]

def correlate(image, kernel):
    """
    Compute the result of correlating the given image with the given kernel.

    The output of this function should have the same form as a 6.009 image (a
    dictionary with 'height', 'width', and 'pixels' keys), but its pixel values
    do not necessarily need to be in the range [0,255], nor do they need to be
    integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    KERNEL REPRESENTATION:
    kernel is a tuple with an int: size, and a tuple K contains (2*size+1)**2 elements.
    e.g. identity kernel 3x3 is rep as (1, (0, 0, 0, 0, 1, 0, 0, 0, 0))
    """
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
    }
    size, K = kernel
    for x in range(image['height']):
        for y in range(image['width']):
            #apply correlation/kernel to pixel (x,y)
            loc = newcolor = 0
            for ix in range(x-size, x+size+1):
                for iy in range(y-size, y+size+1):
                    newcolor += get_pixel_edge(image, ix, iy) * K[loc]
                    loc += 1
            #set_pixel(result, x, y, newcolor)
            result['pixels'].append(newcolor)
    return result


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    for i,color in enumerate(image['pixels']):
        if color < 0: color = 0
        if color > 255: color = 255
        image['pixels'][i] = round(color)

# FILTERS

# box-blur HELPER FUNCTION
def make_blur_kernel(n):
    cells = n*n
    size = n//2
    return (size, (1/cells,)*cells)

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    kernel = make_blur_kernel(n)
    im = correlate(image, kernel)
    round_and_clip_image(im)
    return im

def sharpened(image, n):
    cells = n*n
    size = n//2
    K = (-1/cells,)*(cells//2) + (2-1/cells,) + (-1/cells,)*(cells//2)
    im = correlate(image, (size,K))
    round_and_clip_image(im)
    return im

def edges(image):
    kernel_x = (1, (-1 ,0, 1, -2, 0, 2, -1, 0, 1))
    kernel_y = (1, (-1, -2, -1, 0, 0, 0, 1, 2, 1))
    
    imx = correlate(image, kernel_x)
    imy = correlate(image, kernel_y)

    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [],
    }
    loc = 0
    for x in range(image['height']):
        for y in range(image['width']):
            newcolor = round((imx['pixels'][loc]**2 + imy['pixels'][loc]**2)**0.5)
            result['pixels'].append(newcolor)
            loc += 1
    round_and_clip_image(result)
    return result

# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.

    #sample inverted images
    im = load_image('test_images/bluegill.png')
    im = inverted(im)
    save_image(im, 'test_results/bluegill-inverted.png')
    
    im = load_image('test_images/penguin.png')
    im = inverted(im)
    save_image(im, 'test_results/penguin-inverted.png')

    im = load_image('test_images/python.png')
    im = inverted(im)
    save_image(im, 'test_results/python-inverted.png')

    im = load_image('test_images/frog.png')
    im = inverted(im)
    save_image(im, 'test_results/frog-inverted.png')



    #sample correlated images
    im = load_image('test_images/centered_pixel.png')
    kernel = (1, (0,0,0, 0,1,0, 0,0,0)) #identity
    im = correlate(im, kernel)
    round_and_clip_image(im)
    save_image(im, 'test_results/centered_pixel-correlated.png')

    im = load_image('test_images/pigbird.png')
    kernel = (4, (0,)*18+(1,)+(0,)*62)
    im = correlate(im, kernel)
    round_and_clip_image(im)
    save_image(im, 'test_results/pigbird-correlated.png')

    #sample blurred images
    im = load_image('test_images/cat.png')
    im = blurred(im, 5)
    save_image(im, 'test_results/cat-blurred.png')
    
    im = load_image('test_images/chess.png')
    im = blurred(im, 7)
    save_image(im, 'test_results/chess-blurred.png')

    im = load_image('test_images/penguin.png')
    im = blurred(im, 5)
    save_image(im, 'test_results/penguin-blurred.png')

    #sample sharpened images
    im = load_image('test_images/python.png')
    im = sharpened(im, 3)
    save_image(im, 'test_results/python-sharpened.png')

    im = load_image('test_images/chick.png')
    im = sharpened(im, 7)
    save_image(im, 'test_results/chick-sharpened.png')

    im = load_image('test_images/pp.jpeg')
    im = sharpened(im, 9)
    save_image(im, 'test_results/pp-sharpened.jpeg')


    #sample edge-detection images
    im = load_image('test_images/construct.png')
    im = edges(im)
    save_image(im, 'test_results/construct-edges.png')

    im = load_image('test_images/mushroom.png')
    im = edges(im)
    save_image(im, 'test_results/mushroom-edges.png')

    im = load_image('test_images/pp.jpeg')
    im = edges(im)
    save_image(im, 'test_results/pp-edges.jpeg')

    im = load_image('test_images/frog.png')
    im = edges(im)
    save_image(im, 'test_results/frog-edges.png')

