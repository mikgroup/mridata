
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


def zpad(x, oshape, center=True):
    ishape = x.shape
    y = np.zeros(oshape, dtype=x.dtype)
        
    slc = []
    for i in range(len(ishape)):
        if center:
            slc += [slice(oshape[i] // 2 + math.ceil(-ishape[i] / 2),
                          oshape[i] // 2 + math.ceil(ishape[i] / 2)), ]
        else:
            slc += [slice(0, ishape[i]), ]
    y[tuple(slc)] = x
    
    return y


def crop(x, oshape, center=True):
    ishape = x.shape
    slc = []
    for i in range(len(ishape)):
        if center:
            slc += [slice(ishape[i] // 2 + math.ceil(-oshape[i] / 2),
                          ishape[i] // 2 + math.ceil(oshape[i] / 2)), ]
        else:
            slc += [slice(0, ishape[i]), ]
            
    y = x[slc]
    
    return y
