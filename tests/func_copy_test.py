from unittest.mock import sentinel
import pytest
from src.fixture import *


@pytest.fixture
def namespace():
    class Namespace:
        @property
        def arg(self):
            return sentinel.ARG

        @property
        def default_arg(self):
            return sentinel.DEFAULT_ARG

        @property
        def arg_1(self):
            return sentinel.ARG_1

        @property
        def default_arg_2(self):
            return sentinel.DEFAULT_ARG_2

        @property
        def arg_2(self):
            return sentinel.ARG_2

        @property
        def new_name(self):
            return sentinel.NEW_NAME

        @property
        def new_name_1(self):
            return sentinel.NEW_NAME_1

        @property
        def new_name_2(self):
            return sentinel.NEW_NAME_2

    return Namespace
#
#
# base
#
#


@pytest.fixture
def base_zero_args(namespace):
    def builder():
        @use_fixture_namespace(namespace)
        class BaseTest:
            def test_example(self):
                return sentinel.DEFAULT

        return BaseTest
    return builder


@pytest.fixture
def base_one_arg(namespace):
    def builder():
        @use_fixture_namespace(namespace)
        class BaseTest:
            def test_example(self, arg):
                return arg

        return BaseTest
    return builder


@pytest.fixture
def base_many_args(namespace):
    def builder():
        @use_fixture_namespace(namespace)
        class BaseTest:
            def test_example(self, arg_1, arg_2):
                return arg_1, arg_2

        return BaseTest
    return builder

#
#
# copy
# base_zero_args
#


@pytest.fixture
def copy_zero_arg(namespace, base_zero_args):
    def build():
        @use_fixture_namespace(namespace)
        class CopyTest:
            @func_copy(
                base_zero_args().test_example
            )
            def test_copy(self): pass

        return CopyTest()
    return build


@pytest.fixture
def copy_zero_arg_non_existing(namespace, base_zero_args):
    def build():
        @use_fixture_namespace(namespace)
        class CopyTest:
            @func_copy(
                base_zero_args().test_example,
                map_args={'non_existing_arg': 'new_name'}
            )
            def test_copy(self): pass

        return CopyTest()
    return build


@pytest.fixture
def copy_zero_arg_self(namespace, base_zero_args):
    def build():
        @use_fixture_namespace(namespace)
        class CopyTest:
            @func_copy(
                base_zero_args().test_example,
                map_args={'self': 'new_name'}
            )
            def test_copy(self): pass

        return CopyTest()
    return build

#
#
# base_one_arg
#
#


@pytest.fixture
def copy_one_arg(namespace, base_one_arg):
    def build():
        @use_fixture_namespace(namespace)
        class CopyTest:
            @func_copy(
                base_one_arg().test_example
            )
            def test_copy(self): pass

        return CopyTest()
    return build


@pytest.fixture
def copy_one_arg_non_existing(namespace, base_one_arg):
    def build():
        @use_fixture_namespace(namespace)
        class CopyTest:
            @func_copy(
                base_one_arg().test_example,
                map_args={'non_existing_arg': 'new_name'}
            )
            def test_copy(self): pass

        return CopyTest()
    return build


@pytest.fixture
def copy_one_arg_rename(namespace, base_one_arg):
    def build():
        @use_fixture_namespace(namespace)
        class CopyTest:
            @func_copy(
                base_one_arg().test_example,
                map_args={'arg': 'new_name'}
            )
            def test_copy(self): pass

        return CopyTest()
    return build


@pytest.fixture
def copy_one_arg_self(namespace, base_one_arg):
    def build():
        @use_fixture_namespace(namespace)
        class CopyTest:
            @func_copy(
                base_one_arg().test_example,
                map_args={'self': 'new_name'}
            )
            def test_copy(self): pass

        return CopyTest()
    return build


#
#
# base_many_args
#
#


@pytest.fixture
def copy_many_args(namespace, base_many_args):
    def build():
        @use_fixture_namespace(namespace)
        class CopyTest:
            @func_copy(
                base_many_args().test_example
            )
            def test_copy(self): pass

        return CopyTest()
    return build


@pytest.fixture
def copy_many_args_non_existing(namespace, base_many_args):
    def build():
        @use_fixture_namespace(namespace)
        class CopyTest:
            @func_copy(
                base_many_args().test_example,
                map_args={'non_existing_arg': 'new_name'}
            )
            def test_copy(self): pass

        return CopyTest()
    return build


@pytest.fixture
def copy_many_args_self(namespace, base_many_args):
    def build():
        @use_fixture_namespace(namespace)
        class CopyTest:
            @func_copy(
                base_many_args().test_example,
                map_args={'self': 'new_name'}
            )
            def test_copy(self): pass

        return CopyTest()
    return build


@pytest.fixture
def copy_many_args_rename(namespace, base_many_args):
    def build():
        @use_fixture_namespace(namespace)
        class CopyTest:
            @func_copy(
                base_many_args().test_example,
                map_args={'arg_1': 'new_name_1', 'arg_2': 'new_name_2'}
            )
            def test_copy(self): pass

        return CopyTest()
    return build

#
#
# tests
#
#


def test_base_copy(
    copy_zero_arg,
    copy_one_arg,
    copy_many_args
):
    '''
    GIVEN class X with test_method_x
    AND class Y with test_method_y
    AND X.test_method_x can have default values
    WHEN using @func_copy with X.test_method_x
    THEN inject X.test_method_x code into Y.test_method_y method
    AND default values keep 
    '''
    assert copy_zero_arg().test_copy() == sentinel.DEFAULT
    assert copy_one_arg().test_copy() == sentinel.ARG
    assert copy_many_args().test_copy() == (sentinel.ARG_1, sentinel.ARG_2)


def test_copy_with_rename(
    copy_one_arg_rename,
    copy_many_args_rename
):
    '''
    GIVEN class X with test_method_x
    AND class Y with test_method_y
    AND X.test_method_x can have default values
    WHEN using @func_copy with X.test_method_x
    AND with renaming args
    THEN inject X.test_method_x code into Y.test_method_y method
    AND set args of Y.test_method_y method like X.test_method_x
    AND rename args of X.test_method_x inside Y.test_method_y
    AND rename args of Y.test_method_y
    AND default values keep
    '''
    assert copy_one_arg_rename().test_copy() == sentinel.NEW_NAME
    assert copy_many_args_rename().test_copy() == (
        sentinel.NEW_NAME_1,
        sentinel.NEW_NAME_2
    )


def test_copy_with_self_rename(
    copy_zero_arg_self,
    copy_one_arg_self,
    copy_many_args_self
):
    '''
    GIVEN class X with test_method_x
    AND class Y with test_method_y
    WHEN using @func_copy with X.test_method_x
    AND with renaming self argument
    THEN raise exception
    '''
    msg = 'Cannot rename to/from self arg'

    for builder in [
        copy_zero_arg_self,
        copy_one_arg_self,
        copy_many_args_self
    ]:
        with pytest.raises(ValueError) as excinfo:
            builder().test_copy()
        assert msg in str(excinfo.value)


def test_copy_with_non_existing_args_rename(
    copy_zero_arg_non_existing,
    copy_one_arg_non_existing,
    copy_many_args_non_existing
):
    '''
    GIVEN class X with test_method_x
    AND class Y with test_method_y
    WHEN using @func_copy with X.test_method_x
    AND with renaming non existing arguments inside X.test_method_x
    THEN raise exception
    '''
    msg = 'Argument name does not exists'
    for builder in [
        copy_zero_arg_non_existing,
        copy_one_arg_non_existing,
        copy_many_args_non_existing
    ]:
        with pytest.raises(ValueError) as excinfo:
            builder().test_copy()
        assert msg in str(excinfo.value)
