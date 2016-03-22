# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.python._oldstyle._oldStyle}.
"""

from __future__ import absolute_import, division

import os
import types
import inspect

from twisted.python.reflect import namedAny, fullyQualifiedName
from twisted.python.modules import getModule
from twisted.python.compat import _PY3
from twisted.trial import unittest
from twisted.python._oldstyle import _oldStyle

_skip = None

if _PY3:
    _skip = "Not relevant on Python 3."
elif int(os.environ.get('TWISTED_NEWSTYLE', 0)) == 0:
    _skip = "Not running with TWISTED_NEWSTYLE=1"



class SomeOldStyleClass:
    """
    I am a docstring!
    """



class SomeNewStyleClass(object):
    """
    Some new style class!
    """



class OldStyleDecoratorTests(unittest.TestCase):
    """
    Tests for L{_oldStyle}.
    """

    def test_makesNewStyle(self):
        """
        L{_oldStyle} wraps an old-style class and returns a new-style class
        that descends from the old-style one.
        """
        self.assertEqual(type(SomeOldStyleClass), types.ClassType)
        updatedClass = _oldStyle(SomeOldStyleClass)
        self.assertEqual(type(updatedClass), type)
        self.assertIn(SomeOldStyleClass, updatedClass.__bases__)


    def test_carriesAttributes(self):
        """
        The class returned by L{_oldStyle} has the same C{__name__},
        C{__module__}, and docstring (C{__doc__}) attributes as the original.
        """
        updatedClass = _oldStyle(SomeOldStyleClass)

        self.assertEqual(updatedClass.__name__, SomeOldStyleClass.__name__)
        self.assertEqual(updatedClass.__doc__, SomeOldStyleClass.__doc__)
        self.assertEqual(updatedClass.__module__, SomeOldStyleClass.__module__)


    def test_onlyOldStyleMayBeDecorated(self):
        """
        Using L{_oldStyle} on a new-style class on Python 2 will raise an
        exception.
        """

        with self.assertRaises(ValueError) as e:
            _oldStyle(SomeNewStyleClass)

        self.assertEqual(
            e.exception.args[0],
            ("twisted.python._oldstyle._oldStyle is being used to decorate a "
             "new-style class (twisted.test.test_nooldstyle.SomeNewStyleClass)"
             ". This should only be used to decorate old-style classes."))


    def test_noOpByDefault(self):
        """
        On Python 3 or on Py2 when C{TWISTED_NEWSTYLE} is not set, L{_oldStyle}
        is a no-op.
        """
        updatedClass = _oldStyle(SomeOldStyleClass)
        self.assertIs(updatedClass, SomeOldStyleClass)

    if _PY3:
        test_onlyOldStyleMayBeDecorated.skip = "Only relevant on Py2."

    if _skip:
        test_makesNewStyle.skip = _skip
        test_carriesAttributes.skip = _skip
    else:
        test_noOpByDefault.skip = ("Only relevant when not running under "
                                   "TWISTED_NEWSTYLE=1")


if not _skip:

    class NewStyleOnly(object):
        """
        A base testclass that takes a module and tests if the classes defined
        in it are old-style.

        CAVEATS: This is maybe slightly dumb, and only looks in non-test
        modules (because some test modules have side effects). It also doesn't
        look inside functions, for classes defined there, or nested classes.
        """
        module = None

        def test_newStyleClassesOnly(self):
            """
            Test that C{self.module} has no old-style classes in it.
            """
            try:
                module = namedAny(self.module)
            except ImportError:
                raise unittest.SkipTest("Not importable.")

            for name, val in inspect.getmembers(module):
                if hasattr(val, "__module__") \
                   and val.__module__ == self.module:
                    if isinstance(val, types.ClassType):
                        raise unittest.FailTest(
                            "{val} is an old-style class".format(
                                val=fullyQualifiedName(val)))

    for x in getModule("twisted").walkModules():
        if ".test." in x.name:
            continue

        class Test(NewStyleOnly, unittest.TestCase):
            """
            See L{NewStyleOnly}.
            """
            module = x.name

        acceptableName = x.name.replace(".", "_")
        Test.__name__ = acceptableName
        locals().update({acceptableName: Test})

else:

    class NewStyleOnly(unittest.TestCase):
        """
        Just skip, it doesn't make sense right now.
        """
        def test_newStyleClassesOnly(self):
            """
            No-op.
            """
            raise unittest.SkipTest(skip)