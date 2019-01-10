# Copyright (c) 2018, MeteoSwiss,
# Author: Philipp Meier <philipp.meier@meteoswiss.ch>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
opendap_protocol
================

A pure Python implementation of the OPeNDAP server protocol.

This module allows you to serve arbitrary data structures through the web
framework of your choice as OPeNDAP data objects. It implements just the bare
minimum of the DAP 2.0 protocol: DDS, DAS, and DODS responses and slicing. Array
data needs to be supplied as :class:`numpy.ndarray`.

The classes defined here allow the user to construct a data model in a flexible
way, by describing the data in a hierarchical way using the data types defined
by DAP.

This library only implements the server side encoding. It is tested to serve
clients using the netCDF4 library. PyDAP client libraries are not supported.
"""

import re
import numpy as np

INDENT = '    '
SLICE_CONSTRAINT_RE = r'\[([\d,\W]+)\]$'


class DAPError(Exception):
    pass


class DAPObject(object):
    """A generic DAP object class.
    """

    def __init__(self, name='', parent=None, *args, **kwargs):
        try:
            self.name = '_'.join(name.split(' '))
        except AttributeError:
            self.name = name

        self.children = []
        self.parent = parent

        self.data = None

        self._parse_args(args, kwargs)

    def dds(self, constraint=''):
        if meets_constraint(constraint, self.data_path):
            yield self.ddshead()
            for obj in self.children:
                obj.parent = self
                for stmt in obj.dds(constraint=constraint):
                    yield stmt
            yield self.ddstail()
        return

    def das(self, constraint=''):
        if meets_constraint(constraint, self.data_path):
            yield self.dashead()
            for obj in self.children:
                obj.parent = self
                for stmt in obj.das(constraint=constraint):
                    yield stmt
            yield self.dastail()
        return

    def dods(self, constraint=''):
        if meets_constraint(constraint, self.data_path):
            for stmt in self.dds(constraint=constraint):
                yield stmt.encode()

        yield b'\n'

        if meets_constraint(constraint, self.data_path):
            for stmt in self.dods_data(constraint=constraint):
                yield stmt
        return

    def dods_data(self, constraint=''):

        if meets_constraint(constraint, self.data_path):
            for obj in self.children:
                for stmt in obj.dods_data(constraint=constraint):
                    yield stmt
        return

    def append(self, *obj):
        for o in obj:
            o.parent = self
            self.children.append(o)

    @property
    def indent(self):
        if self.__class__.__name__ == 'Dataset':
            return ''
        else:
            return self.parent.indent + INDENT

    @property
    def data_path(self):
        if self.__class__.__name__ == 'Dataset':
            return ''
        else:
            if self.parent.__class__.__name__ == 'Dataset':
                return self.name
            else:
                return '.'.join([self.parent.data_path, self.name])

    def ddshead(self):
        return '{indent}{obj} {{\n'.format(
            indent=self.indent, obj=self.__class__.__name__)

    def ddstail(self):
        return '{indent}}} {name};\n'.format(
            indent=self.indent, name=self.name)

    def dashead(self):
        name = self.name
        if isinstance(self, Dataset):
            name = 'Attributes'
        return '{indent}{name} {{\n'.format(indent=self.indent, name=name)

    def dastail(self):
        return '{indent}}}\n'.format(indent=self.indent)

    def _parse_args(self, args, kwargs):
        pass


class DAPAtom(DAPObject):
    """A class for handling DAP atomic variables.
    """

    str = None

    def __init__(self, value=None, name=None, parent=None):
        self._val = value
        super(DAPAtom, self).__init__(name=name, parent=parent)

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__class__.__name__

    @classmethod
    def byteorder(cls):
        return np.dtype(cls.dtype.__name__).byteorder

    @classmethod
    def subclasses(cls):
        """Return a list of subclasses.
        """
        return cls.__subclasses__()

    @classmethod
    def type_from_np(cls, nptype):
        """Return the appropriate DAP type for a given numpy dtype.

        :param nptype: A :class:`numpy.dtpye` object

        :returns: A subclass of :class:`DAPAtom`
        """
        for subclass in cls.subclasses():
            if subclass.dtype == nptype:
                return subclass

    def das(self, constraint=''):
        if meets_constraint(constraint, self.data_path):
            yield self.dashead()
            for obj in self.children:
                for stmt in obj.das(constraint=constraint):
                    yield stmt
            yield self.dastail()

    def dds(self, constraint=''):
        if meets_constraint(constraint, self.data_path):
            yield '{indent}{dtype} {name};\n'.format(
                indent=self.indent, dtype=self.__str__(), name=self.name)

    def dods_data(self, constraint=''):
        if meets_constraint(constraint, self.data_path):
            yield dods_encode(self._val, self)


class Byte(DAPAtom):
    dtype = np.ubyte
    str = 'B'


class Int16(DAPAtom):
    dtype = np.int16
    str = '<i4'


class UInt16(DAPAtom):
    dtype = np.uint16
    str = '<u4'


class Int32(DAPAtom):
    dtype = np.int32
    str = '<i4'


class UInt32(DAPAtom):
    dtype = np.uint32
    str = '<u4'


class Float32(DAPAtom):
    dtype = np.float32
    str = '<f4'


class Float64(DAPAtom):
    dtype = np.float64
    str = '<f8'


class String(DAPAtom):
    dtype = np.str
    str = 'S'

    def dods_data(self, constraint=''):
        if meets_constraint(constraint, self.data_path):
            yield dods_encode(self._val.encode('ascii'), self)


class URL(String):
    dtype = np.str
    str = 'S'


class Structure(DAPObject):
    """Class representing a DAP structure.
    """
    pass


class Dataset(Structure):
    """Class representing a DAP dataset.
    """

    def dods_data(self, constraint=''):

        yield b'Data:\r\n'

        for obj in self.children:
            for stmt in obj.dods_data(constraint=constraint):
                yield stmt


class Sequence(DAPObject):
    """Class representing a DAP sequence.
    """

    start_of_inst = b'\x5a\x00\x00\x00'
    end_of_seq = b'\xa5\x00\x00\x00'

    def __init__(self, *args, **kwargs):
        super(Sequence, self).__init__(*args, **kwargs)
        self.schema = None

    def append(self, *item):

        for it in item:
            if it.validates(self.schema):
                it.parent = self
                self.children.append(it)
            else:
                raise DAPError('Item does not validate against the schema.')

    def add_schema(self, schema):
        schema.parent = self
        self.schema = schema

    def das(self, constraint=''):
        if meets_constraint(constraint, self.data_path):
            yield self.dashead()
            for item in self.schema.children:
                item.parent = self
                for stmt in item.das(constraint=constraint):
                    yield stmt
            yield self.dastail()

    def dds(self, constraint=''):
        if meets_constraint(constraint, self.data_path):
            yield self.ddshead()
            for item in self.schema.children:
                item.parent = self
                for stmt in item.dds(constraint=constraint):
                    yield stmt
            yield self.ddstail()

    def dods_data(self, constraint=''):
        if meets_constraint(constraint, self.data_path):
            for obj in self.children:
                yield self.start_of_inst
                for stmt in obj.dods_data(constraint=constraint):
                    yield stmt
            yield self.end_of_seq
        return


class SequenceInstance(DAPObject):
    """Class representing a data item that will be added to a sequence.
    """

    @property
    def data_path(self):
        return self.parent.data_path

    def validates(self, schema):
        """Validate the sequence instance against a sequence schema

        :param schema: A :class:`SequenceSchema` instance.
        """
        # TODO: Implement validataion
        return True

    def dods_data(self, constraint=''):
        for obj in self.children:
            for stmt in obj.dods_data(constraint=constraint):
                yield stmt
        return


class SequenceSchema(DAPObject):
    """Class holding a schema against which SequenceItems are validated.
    """
    pass


class DAPDataObject(DAPObject):
    """A generic class for typed non-atomic objects holding actual data (i.e.
    Array and Grid).
    """

    def _parse_args(self, args, kwargs):

        self.data = kwargs.get('data', None)

        if 'dtype' in kwargs:
            self.dtype = kwargs['dtype']
        else:
            if isinstance(self.data, str):
                self.dtype = String
            else:
                self.dtype = Float64

        if 'dimensions' in kwargs:
            self.dimensions = kwargs['dimensions']
        else:
            self.dimensions = None

    def dods_data(self, constraint=''):

        if meets_constraint(constraint, self.data_path):
            slices = parse_slice_constraint(constraint)
            yield dods_encode(self.data[slices], self.dtype)
            if self.dimensions is not None:
                for i, dim in enumerate(self.dimensions):
                    sl = slices[i] if i < len(slices) else ...
                    yield dods_encode(dim.data[sl], dim.dtype)


class Grid(DAPDataObject):
    def dds(self, constraint=''):
        if meets_constraint(constraint, self.data_path):
            slices = parse_slice_constraint(constraint)
            yield self.ddshead()
            yield self.indent + '  Array:\n'

            yield self.indent + INDENT + \
                  '{dtype} {name}'.format(dtype=self.dtype(), name=self.name)
            for i, dim in enumerate(self.dimensions):
                sl = slices[i] if i < len(slices) else ...
                yield '[{dimname} = {dimlen}]'.format(
                    dimname=dim.name, dimlen=int(np.prod(dim.data[sl].shape)))
            yield ';\n'

            yield self.indent + '  Maps:\n'
            for i, dim in enumerate(self.dimensions):
                orig_parent = dim.parent
                dim.parent = self
                sl = slices[i] if i < len(slices) else ...
                for stmt in dim.dds(constraint='', slicing=sl):
                    yield stmt
                dim.parent = orig_parent
            yield self.ddstail()


class Array(DAPDataObject):
    def dds(self, constraint='', slicing=None):
        if meets_constraint(constraint, self.data_path):
            # Check for slice
            if slicing is None:
                slices = parse_slice_constraint(constraint)
            else:
                slices = slicing

            yield self.indent + \
                  '{dtype} {name}[{name} = {length}];\n' \
                      .format(dtype=self.dtype(),
                              name=self.name,
                              length=int(np.prod(self.data[slices].shape)))


class Attribute(DAPObject):
    def __init__(self, value=None, name=None, dtype=None):
        self.value = value
        self.dtype = dtype
        super(Attribute, self).__init__(name=name)

    def das(self, constraint=''):
        if self.dtype == String:
            d = '"'
        else:
            d = ''

        yield '{indent}{dtype} {name} {d}{value}{d};\n' \
            .format(indent=self.indent,
                    dtype=self.dtype(),
                    name=self.name,
                    value=self.value,
                    d=d)

    def dds(self, *args, **kwargs):
        yield ''


def dods_encode(data, dtype):
    """This is the fast XDR conversion. A 100x100 array takes around 40 micro-
    seconds. This is a speedup of factor 100.
    """

    is_scalar = False
    if not hasattr(data, 'shape'):
        # if not hasattr(data, '__len__'):
        data = np.asarray(data)
        is_scalar = True

    length = np.prod(data.shape)
    packed_length = b''
    if not is_scalar:
        packed_length = length.astype('<i4').byteswap().tostring() * 2

    packed_data = data.astype(dtype.str).byteswap().tostring()

    return packed_length + packed_data


def parse_slice_constraint(constraint):
    """Parses the slicing part of a constraint expression.

    :param constraint: A complete constraint string as received through DAP
                       request.
    :returns: A tuple of slices that can be used for accessing a subdomain of a
              dataset.
    """
    slice_split = re.split(SLICE_CONSTRAINT_RE, constraint)
    if len(slice_split) == 3:
        slice_str = slice_split[1].replace('][', ',')
        return tuple(parse_slice(s) for s in slice_str.split(','))
    else:
        return ...,


def parse_slice(token):
    """Parse a single slice string

    :param token: A string containing a number [3], a range [3:7] or a colon [:]
    :returns: An integer for simple numbers, or a slice object
    """
    try:
        return int(token)
    except ValueError:
        if token == ':':
            return ...
        elif ':' in token:
            rng = [int(s) for s in token.split(':')]
            # The DAP protocol uses slicing including the last index.
            # [0:20] in DAP translates to [0:21] in Python.
            rng[1] += 1
            return slice(*rng)


def meets_constraint(constraint_expr, data_path):
    """Parse the constraint expression and check if data_path meets the
    criteria.

    :param constraint_expr: (string) A DAP constraint string
    :param data_path: (string) Path of a DAP object within the dataset
    :returns: a boolean
    """
    if constraint_expr == '':
        return True

    constraint = constraint_expr.split(',')
    for constr in constraint:
        if constr.startswith(data_path):
            return True

    return False
