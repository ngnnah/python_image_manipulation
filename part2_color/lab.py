#!/usr/bin/env python3

import math

from PIL import Image

# VARIOUS FILTERS

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
    return result

def inverted(image):
    # invert a greyscale image
    return apply_per_pixel(image, lambda c: 255-c)

def color_inverted(image):
    # invert a color image
    return color_filter_from_greyscale_filter(inverted)(image)

##################################################
# HELPER FUNCTIONS FOR color_filter_from_greyscale_filter
def split_rgb(image):
    # Given an color image
    # return a tuple of 3 greyscale images (one for each color component) (R, G, B)
    pixelsRGB = [[], [], []]
    for x in range(image['height']):
        for y in range(image['width']):
            for comp, color in zip(pixelsRGB, get_pixel(image, x, y)):
                comp.append(color)
    return ({
        'height': image['height'],
        'width': image['width'],
        'pixels': comp,} for comp in pixelsRGB)

def recombine_rgb(imR,imG,imB):
    # Given 3 greyscale images (one for each color component) (R, G, B)
    # return a color image, that is a combination of 3 greyscale
    pixels = []
    for x in range(imR['height']):
        for y in range(imR['width']):
            r,g,b = get_pixel(imR, x, y), get_pixel(imG, x, y), get_pixel(imB, x, y)
            pixels.append((r,g,b))
    return {'height': imR['height'],
            'width': imR['width'],
            'pixels': pixels,}
##################################################

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    i.e. split the given color image into its three components, apply the greyscale filter to each,
    and recombine them into a new color image.
    """
    def filter_color_image(im):
        imR, imG, imB = split_rgb(im)
        # apply greyscale filter to each component
        imR, imG, imB = filt(imR), filt(imG), filt(imB)
        return recombine_rgb(imR, imG, imB)
    return filter_color_image

################################################
# MORE HELPER FUNCTIONS FOR APLLYING FILTERS

def get_pixel_edge(image, x, y):
    if x < 0: x = 0
    elif x >= image['height']: x = image['height'] - 1
    if y < 0: y = 0
    elif y >= image['width']: y = image['width'] - 1
    loc = x * image['width'] + y
    return image['pixels'][loc]

def correlate(image, kernel):
    """
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
    """
    for i,color in enumerate(image['pixels']):
        if color < 0: color = 0
        if color > 255: color = 255
        image['pixels'][i] = round(color)

def make_blur_kernel(n):
    # box-blur HELPER FUNCTION
    cells = n*n
    size = n//2
    return (size, (1/cells,)*cells)

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.
    """
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
################################################

def make_blur_filter(n):
    #returns a blur filter (which takes a single image as argument)
    return lambda image: blurred(image, n)

def make_sharpen_filter(n):
    return lambda image: sharpened(image, n)

def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def filter(image):
        for f in filters:
            image = f(image)
        return image
    return filter

# SEAM CARVING

# Main Seam Carving Implementation

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image.
    """
    for _ in range(ncols):
        grey = greyscale_image_from_color_image(image) # this seems to be the only repeated work
        seam = minimum_energy_seam(cumulative_energy_map(compute_energy(grey)))
        image = image_without_seam(image, seam)
    return image

# CREATIVE EXTENSION
def seam_filling(image, ncols):
    """ /TODO
    Opposite of seam_carving
    smart resizing to increase the size of an image by inserting appropriate rows
    at low-energy regions in the image.
    """
    pass
def image_with_new_seam(image,seam):
    pass

def greyscale_vignette(grey):
    height = grey['height']
    width = grey['width']
    import math
    # first, compute the Gaussian Kernel
    #https://docs.opencv.org/2.4/modules/imgproc/doc/filtering.html#Mat%20getGaussianKernel(int%20ksize,%20double%20sigma,%20int%20ktype)
    def getGaussianKernel(ksize):
        sigma = 0.4*((ksize-1)*0.5 - 1) + 0.8
        kernel = []
        scale_factor = 0
        for i in range(ksize):
            coeff = math.e**(-((i-(ksize-1)/2)**2) / (2 * sigma**2))
            kernel.append(coeff)
            scale_factor += coeff
        for i in range(ksize): kernel[i] /= scale_factor
        return kernel
    Kx = getGaussianKernel(width)
    Ky = getGaussianKernel(height)
    K = [k1 * k2 for k1 in Ky for k2 in Kx]
    #http://mathworld.wolfram.com/FrobeniusNorm.html
    # compute the Frobenius matrix norm
    norm = sum(i ** 2 for i in K)
    norm = math.sqrt(norm)
    K = [i* 255/norm for i in K]
    # apply per pixel
    pixels = []
    for coeff, value in zip(K, grey['pixels']):
        pixels.append(coeff*value)
    im = {'height': height, 'width': width, 'pixels': pixels}
    round_and_clip_image(im)
    return im

# Optional Helper Functions for Seam Carving

def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    pixels = [round(.299 * r + .587 * g + .114 * b)
                      for r,g,b in image['pixels']]
    return  {'height': image['height'], 'width': image['width'], 'pixels': pixels,}

def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy"// here: using
    the edges function from last week.
    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)

# HELPER FUNCTION FOR cumulative_energy_map and minimum_energy_seam
def get_min_adj(p, pixels, width):
    '''
    Find the min Energy, and its index, from the 3 "adjacent" pixels in the row above
    '''
    topIndex = p - width #location of the directly above pixel
    top = pixels[topIndex]
    topLeft = pixels[topIndex-1] if p % width != 0 else float('inf')
    topRight = pixels[topIndex+1] if (p+1) % width != 0 else float('inf')
    minIndex, minEnergy = None, float('inf')
    for adj, energy in [(topIndex-1, topLeft), (topIndex, top), (topIndex+1, topRight)]:
            if energy < minEnergy: #Ties is broken by preferring the left-most of the tied columns
                minIndex, minEnergy = adj, energy
    return (minIndex, minEnergy)

def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy function),
    computes a "cumulative energy map".
    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    width, height, pixels = energy['width'], energy['height'], []
    for i in range(height):
        row = range(i * width, (i+1) * width)
        for p in row:
            value = energy['pixels'][p]
            if p >= width: # row 2 and below
                value += get_min_adj(p, pixels, width)[1]
            pixels.append(value)
    return {'height': height, 'width': width, 'pixels': pixels,}


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam: backtracing from the bottom to the top of the cumulative energy map. F
    """
    w, h, pixels = cem['width'], cem['height'], cem['pixels']
    minIndex = min(range(w * (h-1), w * h), key=pixels.__getitem__) # index of min energy in bottom row
    seam = [minIndex]
    for _ in range(h-1):
        minIndex = get_min_adj(minIndex, pixels, w)[0]
        seam = [minIndex] + seam
    return seam

def image_without_seam(im, s):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    s = set(s)
    pixels = []
    for i,value in enumerate(im['pixels']):
        if i not in s: pixels.append(value)
    return  {'height': im['height'], 'width': im['width']-1, 'pixels': pixels,}

# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES
def load_greyscale_image(filename):
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


def save_greyscale_image(image, filename, mode='PNG'):
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

def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}

def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
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

    # color filter, converted from greyscale filter
    im = load_color_image('test_images/cat.png')
    save_color_image(color_inverted(im), 'test_my/cat-color-inverted.png')

    im = load_color_image('test_images/python.png')
    im = color_filter_from_greyscale_filter(make_blur_filter(9))(im)
    save_color_image(im, 'test_my/python-blurred-9.png')

    im = load_color_image('test_images/sparrowchick.png')
    im = color_filter_from_greyscale_filter(make_sharpen_filter(7))(im)
    save_color_image(im, 'test_my/sparrowchick-sharpened-9.png')

    # images resulted from using a cascaded filter (color, or greyscale only, cant be mixed)
    filter1 = color_filter_from_greyscale_filter(edges)
    filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    filt = filter_cascade([filter1, filter1, filter2, filter1])
    im = load_color_image('test_images/frog.png')
    save_color_image(filt(im), 'test_my/frog-cascaded.png')

    # greyscale and color images are separated, i.e. supported by their respective functions
    # to use a greyscale_filter on a color image, first convert it to a color_filter
    # using color_filter_from_greyscale_filter
    filter1 = edges
    filter2 = make_blur_filter(5)
    filt = filter_cascade([filter1, filter1, filter2, filter1])
    im = load_greyscale_image('test_images/frog.png')
    save_greyscale_image(filt(im), 'test_my/frog-cascaded-greyfilters.png')

    # some seam carving images
    im = load_color_image('test_images/twocats.png')
    save_color_image(seam_carving(im,100), 'test_my/twocats-seamcarved100.png')

    # vignette 
    im = load_greyscale_image('test_images/pp.jpeg')
    save_greyscale_image(greyscale_vignette(im), 'test_my/pp-vignette.jpeg')

    im = load_color_image('test_images/pp.jpeg')
    save_color_image(color_filter_from_greyscale_filter(greyscale_vignette)(im), 'test_my/pp-color-vignette.jpeg')

    im = load_color_image('test_images/cat.png')
    save_color_image(color_filter_from_greyscale_filter(greyscale_vignette)(im), 'test_my/cat-vignette.png')

    im = load_color_image('test_images/mushroom.png')
    save_color_image(color_filter_from_greyscale_filter(greyscale_vignette)(im), 'test_my/mushroom-vignette.png')

    im = load_color_image('test_images/chess.png')
    save_color_image(color_filter_from_greyscale_filter(greyscale_vignette)(im), 'test_my/chess-vignette.png')