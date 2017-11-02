import numpy as np
import math
import struct
import warnings


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
            
    y = x[slc].copy()
    
    return y


FLAG_BIG_ENDIAN = 0x01
MAGIC_NUMBER = 8746397786917265778
dtype_kind_to_enum = {'i': 1, 'u': 2, 'f': 3, 'c': 4}
dtype_enum_to_name = {0: 'user', 1: 'int', 2: 'uint', 3: 'float', 4: 'complex'}


def read_ra(f):
    f.open()
    h = getheader(f)
    if h['eltype'] == 0:
        warnings.warn('Unable to convert user data. Returning raw byte string.',
                      UserWarning)
        data = f.read(h['size'])
    else:
        d = '%s%d' % (dtype_enum_to_name[h['eltype']], h['elbyte'] * 8)
        data = np.fromstring(f.read(h['size']), dtype=np.dtype(d))
        data = data.reshape(h['dims'])
    return data


def getheader(f):
    filemagic = f.read(8)
    h = dict()
    h['flags'] = struct.unpack('<Q', f.read(8))[0]
    h['eltype'] = struct.unpack('<Q', f.read(8))[0]
    h['elbyte'] = struct.unpack('<Q', f.read(8))[0]
    h['size'] = struct.unpack('<Q', f.read(8))[0]
    h['ndims'] = struct.unpack('<Q', f.read(8))[0]
    h['dims'] = []
    for d in range(h['ndims']):
        h['dims'].append(struct.unpack('<Q', f.read(8))[0])

    h['dims'] = h['dims'][::-1]
    return h

def write_ra(filename, data):
    flags = 0
    if data.dtype.str[0] == '>':
        flags |= FLAG_BIG_ENDIAN
    try:
        eltype = dtype_kind_to_enum[data.dtype.kind]
    except KeyError:
        eltype = 0
    elbyte = data.dtype.itemsize
    size = data.size * elbyte
    ndims = len(data.shape)
    dims = np.array(data.shape).astype('uint64')
    with open(filename, 'wb') as f:
        f.write(struct.pack('<Q', MAGIC_NUMBER))
        f.write(struct.pack('<Q', flags))
        f.write(struct.pack('<Q', eltype))
        f.write(struct.pack('<Q', elbyte))
        f.write(struct.pack('<Q', size))
        f.write(struct.pack('<Q', ndims))
        f.write(dims[::-1].tobytes())
        f.write(data.tobytes())
