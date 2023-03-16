#!/usr/bin/env python
# -*- coding: utf-8 -*-

from builtins import range
import numpy as np
import scipy.sparse
import PIL.Image
import pyamg


def blend(img_target, img_source, img_mask, offset=(0, 0)):
    """
    Parameters
    ----------
    img_target : np.ndarray
        target image to blend in with. should be atleast the size of the img_source
    img_source : np.ndarray 
        source image to be blended. basically the foreground image
    img_mask : np.ndarray
        mask of hand. preferabbly uint8 mask values of range 0 .. 255
    offset : tuple
        TODO what is this?

    Returns
    -------
    blended image : np.ndarray
        the blended image of img_target and img_source
    
    Notes
    -----
    currently pass the img_target to be atleast of same shape as img_source or bigger. The consideration of size is left to user for now.
    """

    # handling our mask
    if img_mask.ndim == 3:
        img_mask = img_mask[:, :, 0]
    
    if img_mask.max() <= 1:
        img_mask *= 255
        img_mask = img_mask.astype(np.uint8)

    # compute regions to be blended
    region_source = (
        max(-offset[0], 0),
        max(-offset[1], 0),
        min(img_target.shape[0] - offset[0], img_source.shape[0]),
        min(img_target.shape[1] - offset[1], img_source.shape[1]))
    region_target = (
        max(offset[0], 0),
        max(offset[1], 0),
        min(img_target.shape[0], img_source.shape[0] + offset[0]),
        min(img_target.shape[1], img_source.shape[1] + offset[1]))
    region_size = (region_source[2] - region_source[0], region_source[3] - region_source[1])

    # clip and normalize mask image
    img_mask = img_mask[region_source[0]:region_source[2], region_source[1]:region_source[3]]
    img_mask[img_mask == 0] = False
    img_mask[img_mask != False] = True

    # determines the diagonals on the coefficient matrix
    positions = np.where(img_mask)
    # setting the positions to be in a flatted manner
    positions = (positions[0] * region_size[1]) + positions[1]

    # row and col size of coefficient matrix
    n = np.prod(region_size)

    main_diagonal = np.ones(n)
    main_diagonal[positions] = 4
    diagonals = [main_diagonal]
    diagonals_positions = [0]

    # creating the diagonals of the coefficient matrix
    for diagonal_pos in [-1, 1, -region_size[1], region_size[1]]:
        in_bounds_indices = None
        if np.any(positions + diagonal_pos > n):
            in_bounds_indices = np.where(positions + diagonal_pos < n)[0]
        elif np.any(positions + diagonal_pos < 0):
            in_bounds_indices = np.where(positions + diagonal_pos >= 0)[0]
        in_bounds_positions = positions[in_bounds_indices]

        # create diagonal
        temp_diagonal_index = in_bounds_positions + diagonal_pos
        # check if the diagonal is in bounds
        temp_diagonal_index = temp_diagonal_index[np.where(temp_diagonal_index < n)]
        # check if it is not empty 
        if not temp_diagonal_index.size == 0:
            diagonal = np.zeros(n)
            diagonal[temp_diagonal_index] = -1
            diagonals.append(diagonal)
            diagonals_positions.append(diagonal_pos)
    A = scipy.sparse.spdiags(diagonals, diagonals_positions, n, n, 'csr')

    # create poisson matrix for b
    P = pyamg.gallery.poisson(img_mask.shape) 

    # get positions in mask that should be taken from the target
    inverted_img_mask = np.invert(img_mask.astype(bool)).flatten()
    positions_from_target = np.where(inverted_img_mask)[0]

    # for each layer (ex. RGB)
    for num_layer in range(img_target.shape[2]):
        # get subimages
        t = img_target[region_target[0]:region_target[2], region_target[1]:region_target[3], num_layer]
        s = img_source[region_source[0]:region_source[2], region_source[1]:region_source[3], num_layer]
        t = t.flatten()
        s = s.flatten()

        # create b
        b = P * s
        b[positions_from_target] = t[positions_from_target]

        # solve Ax = b
        x = scipy.sparse.linalg.spsolve(A, b)

        # assign x to target image
        x = np.reshape(x, region_size)
        x = np.clip(x, 0, 255)
        x = np.array(x, img_target.dtype)
        img_target[region_target[0]:region_target[2], region_target[1]:region_target[3], num_layer] = x

    return img_target[region_target[0]:region_target[2], region_target[1]:region_target[3], :]

def test():
    img_mask = np.asarray(PIL.Image.open('./testimages/test1_mask.png'))
    img_mask.flags.writeable = True
    img_source = np.asarray(PIL.Image.open('./testimages/test1_src.png'))
    img_source.flags.writeable = True
    img_target = np.asarray(PIL.Image.open('./testimages/test1_target.png'))
    img_target.flags.writeable = True
    img_ret = blend(img_target, img_source, img_mask, offset=(40, -30))
    img_ret = PIL.Image.fromarray(np.uint8(img_ret))
    img_ret.save('./testimages/test1_ret.png')


if __name__ == '__main__':
    test()