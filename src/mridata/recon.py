
import numpy as np
import math


def rss(x, axes=(0, )):

    return np.sum(np.abs(x)**2, axis=axes)**0.5


def fftc(x, axes=None):
    return np.fft.fftshift(np.fft.fftn(np.fft.ifftshift(x, axes=axes),
                                       axes=axes, norm='ortho'), axes=axes)


def ifftc(x, axes=None):
    
    return np.fft.fftshift(np.fft.ifftn(np.fft.ifftshift(x, axes=axes),
                                        axes=axes, norm='ortho'), axes=axes)


def _expand_shapes(*shapes):

    shapes = [list(shape) for shape in shapes]
    max_ndim = max(len(shape) for shape in shapes)
    shapes_exp = [[1] * (max_ndim - len(shape)) + shape
                  for shape in shapes]

    return tuple(shapes_exp)


def resize(input, oshape, ishift=None, oshift=None):
    """Resize with zero-padding or cropping.

    Args:
        input (array): Input array.
        oshape (tuple of ints): Output shape.
        ishift (None or tuple of ints): Input shift.
        oshift (None or tuple of ints): Output shift.

    Returns:
        array: Zero-padded or cropped result.
    """

    ishape_exp, oshape_exp = _expand_shapes(input.shape, oshape)

    if ishape_exp == oshape_exp:
        return input.reshape(oshape)

    if ishift is None:
        ishift = [max(i // 2 - o // 2, 0)
                  for i, o in zip(ishape_exp, oshape_exp)]

    if oshift is None:
        oshift = [max(o // 2 - i // 2, 0)
                  for i, o in zip(ishape_exp, oshape_exp)]

    copy_shape = [min(i - si, o - so) for i, si, o, so in zip(ishape_exp, ishift,
                                                              oshape_exp, oshift)]
    islice = tuple([slice(si, si + c) for si, c in zip(ishift, copy_shape)])
    oslice = tuple([slice(so, so + c) for so, c in zip(oshift, copy_shape)])

    output = np.zeros(oshape_exp, dtype=input.dtype)
    input = input.reshape(ishape_exp)
    output[oslice] = input[islice]

    return output.reshape(oshape)
