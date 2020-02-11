#!/usr/bin/env python3

import os
import lab
import pickle
import hashlib
import unittest
import collections

TEST_DIRECTORY = os.path.dirname(__file__)


def object_hash(x):
    return hashlib.sha512(pickle.dumps(x)).hexdigest()


class Lab1Test(unittest.TestCase):
    def compare_greyscale_images(self, im1, im2):
        self.assertTrue(set(im1.keys()) == {'height', 'width', 'pixels'}, 'Incorrect keys in dictionary')
        self.assertEqual(im1['height'], im2['height'], 'Heights must match')
        self.assertEqual(im1['width'], im2['width'], 'Widths must match')
        self.assertEqual(len(im1['pixels']), im1['height']*im1['width'], 'Incorrect number of pixels')
        pix_incorrect = (None, None)
        for ix, (i, j) in enumerate(zip(im1['pixels'], im2['pixels'])):
            if i != j:
                pix_incorrect = (ix, abs(i-j))
        self.assertTrue(pix_incorrect == (None, None), 'Pixels must match.  Incorrect value at location %s (differs from expected by %s)' % pix_incorrect)

    def compare_color_images(self, im1, im2):
        self.assertTrue(set(im1.keys()) == {'height', 'width', 'pixels'}, 'Incorrect keys in dictionary')
        self.assertEqual(im1['height'], im2['height'], 'Heights must match')
        self.assertEqual(im1['width'], im2['width'], 'Widths must match')
        self.assertEqual(len(im1['pixels']), im1['height']*im1['width'], 'Incorrect number of pixels')
        self.assertTrue(all(isinstance(i, tuple) and len(i)==3 for i in im1['pixels']), 'Pixels must all be 3-tuples')
        self.assertTrue(all(0<=subi<=255 for i in im1['pixels'] for subi in i), 'Pixels values must all be in the range from [0, 255]')
        pix_incorrect = (None, None)
        for ix, (i, j) in enumerate(zip(im1['pixels'], im2['pixels'])):
            if i != j:
                tup_diff = tuple(abs(i[t]-j[t]) for t in {0,1,2})
                pix_incorrect = (ix, tup_diff)
        self.assertTrue(pix_incorrect == (None, None), f'Pixels must match.  Incorrect value at location %s (differs from expected by %s)' % pix_incorrect)


class TestImage(Lab1Test):
    def test_load_color(self):
        result = lab.load_color_image('test_images/centered_pixel.png')
        expected = {
            'height': 11,
            'width': 11,
            'pixels': [(244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (253, 253, 149), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198)]
        }
        self.compare_color_images(result, expected)

class TestColorFilters(Lab1Test):
    def test_color_filter_inverted(self):
        im = lab.load_color_image('test_images/centered_pixel.png')
        color_inverted = lab.color_filter_from_greyscale_filter(lab.inverted)
        self.assertTrue(callable(color_inverted), 'color_filter_from_greyscale_filter should return a function.')
        result = color_inverted(im)
        expected = {
            'height': 11,
            'width': 11,
            'pixels': [(11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                       (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                       (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                       (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                       (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                       (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),  (2, 2, 106), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                       (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                       (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                       (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                       (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57),
                       (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57), (11, 82, 57)]
        }
        self.compare_color_images(result, expected)

    def test_color_filter_edges(self):
        im = lab.load_color_image('test_images/centered_pixel.png')
        color_edges = lab.color_filter_from_greyscale_filter(lab.edges)
        self.assertTrue(callable(color_edges), 'color_filter_from_greyscale_filter should return a function.')
        result = color_edges(im)
        expected = {
            'height': 11,
            'width': 11,
            'pixels': [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                       (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                       (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                       (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                       (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (13, 113, 69), (18, 160, 98), (13, 113, 69), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                       (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (18, 160, 98), (0, 0, 0), (18, 160, 98), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                       (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (13, 113, 69), (18, 160, 98), (13, 113, 69), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                       (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                       (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                       (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                       (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
        }
        self.compare_color_images(result, expected)

    def test_color_filters(self):
        for fname in ('frog', 'tree'):
            for filt, filt_name in {(lab.edges, 'edges'), (lab.inverted, 'inverted')}:
                with self.subTest(f=fname):
                    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', f'{fname}.png')
                    expfile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_{filt_name}.png')
                    im = lab.load_color_image(inpfile)
                    oim = object_hash(im)
                    color_filter = lab.color_filter_from_greyscale_filter(filt)
                    self.assertTrue(callable(color_filter), 'color_filter_from_greyscale_filter should return a function.')
                    result = color_filter(im)
                    expected = lab.load_color_image(expfile)
                    self.assertEqual(object_hash(im), oim, 'Be careful not to modify the original image!')
                    self.compare_color_images(result, expected)

    def test_blur_filter_1(self):
        blur_filter = lab.make_blur_filter(3)
        self.assertTrue(callable(blur_filter), 'make_blur_filter should return a function.')
        color_blur = lab.color_filter_from_greyscale_filter(blur_filter)
        im = lab.load_color_image('test_images/centered_pixel.png')
        result = color_blur(im)
        expected = {
            'height': 11,
            'width': 11,
            'pixels': [(244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (245, 182, 193), (245, 182, 193), (245, 182, 193), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (245, 182, 193), (245, 182, 193), (245, 182, 193), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (245, 182, 193), (245, 182, 193), (245, 182, 193), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198),
                       (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198), (244, 173, 198)]
        }
        self.compare_color_images(result, expected)


    def test_blur_filters(self):
        for fname in ('cat', 'mushroom'):
            for ker_size in {3, 5}:
                with self.subTest(f=fname):
                    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', f'{fname}.png')
                    expfile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_blurred{ker_size}.png')
                    im = lab.load_color_image(inpfile)
                    oim = object_hash(im)
                    blur_filter = lab.make_blur_filter(ker_size)
                    self.assertTrue(callable(blur_filter), 'make_blur_filter should return a function.')
                    color_blur = lab.color_filter_from_greyscale_filter(blur_filter)
                    result = color_blur(im)
                    expected = lab.load_color_image(expfile)
                    self.assertEqual(object_hash(im), oim, 'Be careful not to modify the original image!')
                    self.compare_color_images(result, expected)


    def test_sharpen_filters(self):
        for fname in ('construct', 'bluegill'):
            for ker_size in {3, 5}:
                with self.subTest(f=fname):
                    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', f'{fname}.png')
                    expfile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_sharpened{ker_size}.png')
                    im = lab.load_color_image(inpfile)
                    oim = object_hash(im)
                    sharpened_filter = lab.make_sharpen_filter(ker_size)
                    self.assertTrue(callable(sharpened_filter), 'make_sharpen_filter should return a function.')
                    color_sharpen = lab.color_filter_from_greyscale_filter(sharpened_filter)
                    result = color_sharpen(im)
                    expected = lab.load_color_image(expfile)
                    self.assertEqual(object_hash(im), oim, 'Be careful not to modify the original image!')
                    self.compare_color_images(result, expected)


class TestCascade(Lab1Test):
    def setUp(self):
        self.color_edges = lab.color_filter_from_greyscale_filter(lab.edges)
        self.color_inverted = lab.color_filter_from_greyscale_filter(lab.inverted)
        self.color_blur_5 = lab.color_filter_from_greyscale_filter(lab.make_blur_filter(5))

    def test_cascade_1(self):
        im = lab.load_color_image('test_images/centered_pixel.png')
        f1 = self.color_edges
        f2 = self.color_inverted
        f3 = self.color_blur_5
        expected = {
            'height': 11,
            'width': 11,
            'pixels': [(255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255),
                       (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255),
                       (255, 255, 255), (255, 255, 255), (254, 250, 252), (254, 244, 248), (253, 240, 246), (253, 240, 246), (253, 240, 246), (254, 244, 248), (254, 250, 252), (255, 255, 255), (255, 255, 255),
                       (255, 255, 255), (255, 255, 255), (254, 244, 248), (253, 238, 244), (252, 227, 238), (252, 227, 238), (252, 227, 238), (253, 238, 244), (254, 244, 248), (255, 255, 255), (255, 255, 255),
                       (255, 255, 255), (255, 255, 255), (253, 240, 246), (252, 227, 238), (250, 211, 228), (250, 211, 228), (250, 211, 228), (252, 227, 238), (253, 240, 246), (255, 255, 255), (255, 255, 255),
                       (255, 255, 255), (255, 255, 255), (253, 240, 246), (252, 227, 238), (250, 211, 228), (250, 211, 228), (250, 211, 228), (252, 227, 238), (253, 240, 246), (255, 255, 255), (255, 255, 255),
                       (255, 255, 255), (255, 255, 255), (253, 240, 246), (252, 227, 238), (250, 211, 228), (250, 211, 228), (250, 211, 228), (252, 227, 238), (253, 240, 246), (255, 255, 255), (255, 255, 255),
                       (255, 255, 255), (255, 255, 255), (254, 244, 248), (253, 238, 244), (252, 227, 238), (252, 227, 238), (252, 227, 238), (253, 238, 244), (254, 244, 248), (255, 255, 255), (255, 255, 255),
                       (255, 255, 255), (255, 255, 255), (254, 250, 252), (254, 244, 248), (253, 240, 246), (253, 240, 246), (253, 240, 246), (254, 244, 248), (254, 250, 252), (255, 255, 255), (255, 255, 255),
                       (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255),
                       (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255)]
        }
        f_cascade = lab.filter_cascade([f1, f2, f3])
        self.assertTrue(callable(f_cascade), 'filter_cascade should return a function.')
        result = f_cascade(im)
        self.compare_color_images(result, expected)

    def test_cascades(self):
        cascade0 = [self.color_edges,
                    lab.color_filter_from_greyscale_filter(lab.make_sharpen_filter(3))]
        cascade1 = [lab.color_filter_from_greyscale_filter(lab.make_blur_filter(5)),
                    self.color_edges,
                    lab.color_filter_from_greyscale_filter(lab.make_sharpen_filter(3))]
        cascade3 = [self.color_edges]*5 + [self.color_inverted]
        for fname in ('tree',):
            for cix, cascade in enumerate([cascade0, cascade1]):
                inpfile = os.path.join(TEST_DIRECTORY, 'test_images', f'{fname}.png')
                expfile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_cascade{cix}.png')
                im = lab.load_color_image(inpfile)
                oim = object_hash(im)
                f_cascade = lab.filter_cascade(cascade)
                self.assertTrue(callable(f_cascade), 'filter_cascade should return a function.')
                result = f_cascade(im)
                expected = lab.load_color_image(expfile)
                self.assertEqual(object_hash(im), oim, 'Be careful not to modify the original image!')
                self.compare_color_images(result, expected)

class TestSeamCarvingHelpers(Lab1Test):
    def test_greyscale(self):
        for fname in ('pattern', 'smallfrog', 'bluegill', 'twocats', 'tree'):
            inpfile = os.path.join(TEST_DIRECTORY, 'test_images', f'{fname}.png')
            im = lab.load_color_image(inpfile)
            oim = object_hash(im)

            grey = lab.greyscale_image_from_color_image(im)

            expfile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_grey.png')
            self.assertEqual(object_hash(im), oim, 'Be careful not to modify the original image!')
            self.compare_greyscale_images(grey, load_greyscale_image(expfile))

    def test_energy(self):
        for fname in ('pattern', 'smallfrog', 'bluegill', 'twocats', 'tree'):
            inpfile = os.path.join(TEST_DIRECTORY, 'test_images', f'{fname}.png')
            im = load_greyscale_image(inpfile)
            oim = object_hash(im)
            result = lab.compute_energy(im)

            expfile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_energy.pickle')
            with open(expfile, 'rb') as f:
                energy = pickle.load(f)

            self.compare_greyscale_images(result, energy)

    def test_cumulative_energy(self):
        for fname in ('pattern', 'smallfrog', 'bluegill', 'twocats', 'tree'):
            infile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_energy.pickle')
            with open(infile, 'rb') as f:
                energy = pickle.load(f)
            result = lab.cumulative_energy_map(energy)

            expfile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_cumulative_energy.pickle')
            with open(expfile, 'rb') as f:
                cem = pickle.load(f)

            self.compare_greyscale_images(result, cem)

    def test_min_seam_indices(self):
        for fname in ('pattern', 'smallfrog', 'bluegill', 'twocats', 'tree'):
            infile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_cumulative_energy.pickle')
            with open(infile, 'rb') as f:
                cem = pickle.load(f)
            result = lab.minimum_energy_seam(cem)

            expfile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_minimum_energy_seam.pickle')
            with open(expfile, 'rb') as f:
                seam = pickle.load(f)

            self.assertEqual(len(result), len(seam))
            self.assertEqual(set(result), set(seam))

    def test_seam_removal(self):
        for fname in ('pattern', 'bluegill', 'twocats', 'tree'):
            infile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_minimum_energy_seam.pickle')
            with open(infile, 'rb') as f:
                seam = pickle.load(f)

            imfile = os.path.join(TEST_DIRECTORY, 'test_images', f'{fname}.png')
            result = lab.image_without_seam(lab.load_color_image(imfile), seam)

            expfile = os.path.join(TEST_DIRECTORY, 'test_results', f'{fname}_1seam.png')

            self.compare_color_images(result, lab.load_color_image(expfile))


class TestSeamCarving(Lab1Test):
    def test_endtoend_centeredpixel(self):
        inpfile = os.path.join(TEST_DIRECTORY, 'test_images', 'centered_pixel.png')

        im = lab.load_color_image(inpfile)
        oim = object_hash(im)

        for i in range(1, 11):
            result = lab.seam_carving(im, i)
            self.assertEqual(object_hash(im), oim, 'Be careful not to modify the original image!')

            expfile = os.path.join(TEST_DIRECTORY, 'test_results', 'seams_centered_pixel', f'{i:02d}.png')
            self.compare_color_images(result, lab.load_color_image(expfile))


    def test_endtoend_pattern(self):
        inpfile = os.path.join(TEST_DIRECTORY, 'test_images', 'pattern.png')

        im = lab.load_color_image(inpfile)
        oim = object_hash(im)

        for i in range(1, 9):
            result = lab.seam_carving(im, i)
            self.assertEqual(object_hash(im), oim, 'Be careful not to modify the original image!')

            expfile = os.path.join(TEST_DIRECTORY, 'test_results', 'seams_pattern', f'{i:02d}.png')
            self.compare_color_images(result, lab.load_color_image(expfile))


    def test_endtoend_smallfrog(self):
        inpfile = os.path.join(TEST_DIRECTORY, 'test_images', 'smallfrog.png')

        im = lab.load_color_image(inpfile)
        oim = object_hash(im)

        for i in range(1, 31):
            result = lab.seam_carving(im, i)
            self.assertEqual(object_hash(im), oim, 'Be careful not to modify the original image!')

            expfile = os.path.join(TEST_DIRECTORY, 'test_results', 'seams_smallfrog', f'{i:02d}.png')
            self.compare_color_images(result, lab.load_color_image(expfile))


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    from PIL import Image
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


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
