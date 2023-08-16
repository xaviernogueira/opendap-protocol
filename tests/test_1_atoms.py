"""Pytest suite to make sure that for all Atomic variables only valid
instances can be created
"""
from opendap_protocol import atoms
import numpy as np


def test_ubytes() -> None:
    """Test that the ubyte class only allows valid instances"""

    # Test that the ubyte class only allows valid instances
    b = atoms.Bytes(np.ubyte(0))
    assert b.value == 0
    assert b.string == 'B'
    assert atoms.Bytes(np.ubyte(255)).value == 255
    assert atoms.Bytes(np.ubyte(1.9)).value == 1

    try:
        atoms.Bytes(1)
        assert False
    except ValueError:
        assert True
    try:
        atoms.Bytes('not_byte')
        assert False
    except ValueError:
        assert True
    try:
        atoms.Bytes(-1)
        assert False
    except ValueError:
        assert True


def test_int16() -> None:
    """Test Int16 atomic type"""

    # Test that the ubyte class only allows valid instances
    i = atoms.Int16(np.int16(0))
    assert i.value == 0
    assert i.string == '>i4'
    assert atoms.Int16(np.int16(-32768)).value == -32768
    assert atoms.Int16(np.int16(32767)).value == 32767

    try:
        atoms.Int16(32768)
        assert False
    except ValueError:
        assert True
    try:
        atoms.Int16(-32769)
        assert False
    except ValueError:
        assert True
    try:
        atoms.Int16('not_int16')
        assert False
    except ValueError:
        assert True


def test_uint16() -> None:
    """Test UInt16 atomic type"""

    # Test that the ubyte class only allows valid instances
    i = atoms.UInt16(np.uint16(0))
    assert i.value == 0
    assert i.string == '>u4'
    assert atoms.UInt16(np.uint16(65535)).value == 65535

    try:
        atoms.UInt16(65536)
        assert False
    except ValueError:
        assert True
    try:
        atoms.UInt16(-1)
        assert False
    except ValueError:
        assert True
    try:
        atoms.UInt16('not_uint16')
        assert False
    except ValueError:
        assert True


def test_int32() -> None:
    """Test Int32 atomic type"""

    # Test that the ubyte class only allows valid instances
    i = atoms.Int32(np.int32(0))
    assert i.value == 0
    assert i.string == '>i4'
    assert atoms.Int32(np.int32(-2147483648)).value == -2147483648
    assert atoms.Int32(np.int32(2147483647)).value == 2147483647

    try:
        atoms.Int32(2147483648)
        assert False
    except ValueError:
        assert True
    try:
        atoms.Int32(-2147483649)
        assert False
    except ValueError:
        assert True
    try:
        atoms.Int32('not_int32')
        assert False
    except ValueError:
        assert True


def test_uint32() -> None:
    """Test UInt32 atomic type"""

    # Test that the ubyte class only allows valid instances
    i = atoms.UInt32(np.uint32(0))
    assert i.value == 0
    assert i.string == '>u4'
    assert atoms.UInt32(np.uint32(4294967295)).value == 4294967295

    try:
        atoms.UInt32(4294967296)
        assert False
    except ValueError:
        assert True
    try:
        atoms.UInt32(-1)
        assert False
    except ValueError:
        assert True
    try:
        atoms.UInt32('not_uint32')
        assert False
    except ValueError:
        assert True


def test_float32() -> None:
    """Test Float32 atomic type"""

    # Test that the ubyte class only allows valid instances
    f = atoms.Float32(np.float32(0))
    assert f.value == 0
    assert f.string == '>f4'
    assert atoms.Float32(np.float32(100.0)).value == 100.0

    try:
        atoms.Float32(3.4028235e+38 * 2)
        assert False
    except ValueError:
        assert True
    try:
        atoms.Float32(-3.4028235e+38 * 2)
        assert False
    except ValueError:
        assert True
    try:
        atoms.Float32('not_float32')
        assert False
    except ValueError:
        assert True


def test_float64() -> None:
    """Test Float64 atomic type"""

    # Test that the ubyte class only allows valid instances
    f = atoms.Float64(np.float64(0.0))
    assert f.value == 0.0
    assert f.string == '>f8'
    assert atoms.Float64(np.float64(-100.0)).value == -100.0

    try:
        atoms.Float64(0)
        assert False
    except ValueError:
        assert True
    try:
        atoms.Float64('not_float64')
        assert False
    except ValueError:
        assert True


def test_string() -> None:
    """Test String atomic type"""

    # Test that the ubyte class only allows valid instances
    s = atoms.String('test')
    assert s.value == 'test'
    assert s.string == 'S'

    # try a non-ascii string
    non_ascii = '§'
    try:
        atoms.String(non_ascii)
        assert False
    except ValueError:
        assert True
    try:
        atoms.String(1)
        assert False
    except ValueError:
        assert True


def test_url() -> None:
    """Test URL atomic type"""

    # Test that the ubyte class only allows valid instances
    valid_url = r'http://www.cwi.nl:80/%7Eguido/Python.html'
    url = atoms.URL(valid_url)
    assert url.value == valid_url
    assert url.string == 'S'

    # try invalid string url
    try:
        atoms.URL('/data/Python.html')
        assert False
    except ValueError:
        assert True

    # try invalid type
    try:
        atoms.URL(1.0)
        assert False
    except ValueError:
        assert True


test_uint32()

# test_ubytes()
# test_url()
