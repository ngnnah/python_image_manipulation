#!/usr/bin/env python3

import os
import lab
import pickle
import hashlib
import unittest

TEST_DIRECTORY = os.path.dirname(__file__)


def object_hash(x):
    return hashlib.sha512(pickle.dumps(x)).hexdigest()


class Lab0Test(unittest.TestCase):
    def compare_images(self, im1, im2):
        self.assertTrue(set(im1.keys()) == {'height', 'width', 'pixels'}, 'Incorrect keys in dictionary')
        self.assertEqual(im1['height'], im2['height'], 'Heights must match')
        self.assertEqual(im1['width'], im2['width'], 'Widths must match')
        self.assertEqual(len(im1['pixels']), im1['height']*im1['width'], 'Incorrect number of pixels')
        self.assertTrue(all(isinstance(i, int) for i in im1['pixels']), 'Pixels must all be integers')
        self.assertTrue(all(0<=i<=255 for i in im1['pixels']), 'Pixels must all be in the range from [0, 255]')
        pix_incorrect = (None, None)
        for ix, (i, j) in enumerate(zip(im1['pixels'], im2['pixels'])):
            if i != j:
                pix_incorrect = (ix, abs(i-j))
        self.assertTrue(pix_incorrect == (None, None), 'Pixels must match.  Incorrect value at location %s (differs from expected by %s)' % pix_incorrect)


class TestImage(Lab0Test):
    def test_load(self):
        result = lab.load_image('test_images/centered_pixel.png')
        expected = {
            'height': 11,
            'width': 11,
            'pixels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 255, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        }
        self.compare_images(result, expected)


class TestInverted(Lab0Test):
    def test_inverted_1(self):
        im = lab.load_image('test_images/centered_pixel.png')
        result = lab.inverted(im)
        expected = {
            'height': 11,
            'width': 11,
            'pixels': [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 0, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                       255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255],
        }
        self.compare_images(result, expected)

    def test_inverted_2(self):
        im = {'height': 1, 'width': 4, 'pixels': [8, 96, 142, 211]}
        result = lab.inverted(im)
        expected = {
            'height': 1, 
            'width': 4, 
            'pixels': [247,159,113,44],
        }
        self.compare_images(result, expected)

    def test_inverted_3(self):
        im = {
            'height': 2, 
            'width': 4, 
            'pixels': [8, 96, 142, 211, 
                       8, 96, 142, 211]
        }
        result = lab.inverted(im)
        expected = {
            'height': 2, 
            'width': 4, 
            'pixels': [247,159,113,44, 
                       247,159,113,44],
        }
        self.compare_images(result, expected)

    def test_inverted_images(self):
        for fname in ('mushroom', 'twocats', 'chess'):
            with self.subTest(f=fname):
                inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
                expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_invert.png' % fname)
                im = lab.load_image(inpfile)
                oim = object_hash(im)
                result = lab.inverted(im)
                expected = lab.load_image(expfile)
                self.assertEqual(object_hash(im), oim, 'Be careful not to modify the original image!')
                self.compare_images(result, expected)
class TestCorrelation(Lab0Test):
    def test_correlation1(self):
        im = {'height': 3, 'width': 3, 'pixels': [0,0,0, 0,255,0, 0,0,0]}
        kernel = (1, (0,0,0, 0,1,0, 0,0,0)) #identity
        result = lab.correlate(im, kernel)
        expected = {'height': 3, 'width': 3, 'pixels': [0,0,0, 0,255,0, 0,0,0]}
        self.compare_images(result, expected)

class TestFilters(Lab0Test):
    def test_blurred(self):
        for kernsize in (1, 3, 7):
            for fname in ('mushroom', 'twocats', 'chess'):
                with self.subTest(k=kernsize, f=fname):
                    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
                    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_blur_%02d.png' % (fname, kernsize))
                    input_img = lab.load_image(inpfile)
                    input_hash = object_hash(input_img)
                    result = lab.blurred(input_img, kernsize)
                    expected = lab.load_image(expfile)
                    self.assertEqual(object_hash(input_img), input_hash, "Be careful not to modify the original image!")
                    self.compare_images(result, expected)

    def test_blurred_black_image(self):
        im = {'height': 5, 'width': 6, 'pixels': [0]*30}
        for size in (3,7):
            result = lab.blurred(im, size)
            self.compare_images(result, im)
        

    def test_blurred_centered_pixel(self):
        im = lab.load_image('test_images/centered_pixel.png')
        for size in (1,3):
            result = lab.blurred(im, size)
            if size == 1:
                expected = im
            else:
                expected = {
                    'height': 11,
                    'width': 11,
                    'pixels': [0]*44 + [0,0,0,0, 28,28,28, 0,0,0,0]*3 + [0]*44,
                }
            self.compare_images(result, expected)

    def test_sharpened(self):
        for kernsize in (1, 3, 9):
            for fname in ('mushroom', 'twocats', 'chess'):
                with self.subTest(k=kernsize, f=fname):
                    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
                    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_sharp_%02d.png' % (fname, kernsize))
                    input_img = lab.load_image(inpfile)
                    input_hash = object_hash(input_img)
                    result = lab.sharpened(input_img, kernsize)
                    expected = lab.load_image(expfile)
                    self.assertEqual(object_hash(input_img), input_hash, "Be careful not to modify the original image!")
                    self.compare_images(result, expected)

    def test_edges(self):
        for fname in ('mushroom', 'twocats', 'chess'):
            with self.subTest(f=fname):
                inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
                expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_edges.png' % fname)
                input_img = lab.load_image(inpfile)
                input_hash = object_hash(input_img)
                result = lab.edges(input_img)
                expected = lab.load_image(expfile)
                self.assertEqual(object_hash(input_img), input_hash, "Be careful not to modify the original image!")
                self.compare_images(result, expected)

    def test_edges_centered_pixel(self):
        im = lab.load_image('test_images/centered_pixel.png')
        result = lab.edges(im)
        expected = {'height': 11, 'width': 11, 
            'pixels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 255, 0, 255, 0, 0, 
                    0, 0, 0, 0, 0, 0, 255, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
        self.compare_images(result, expected)

if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
