from unittest.mock import sentinel
import pytest_cases
from src import *


@pytest_cases.fixture
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


@pytest_cases.fixture
def base_zero_args(namespace):
    @use_fixture_namespace(namespace)
    class BaseTest:
        def test_example(self):
            return sentinel.DEFAULT

    return BaseTest


@pytest_cases.fixture
def base_one_arg(namespace):
    @use_fixture_namespace(namespace)
    class BaseTest:
        def test_example(self, arg):
            return arg

    return BaseTest


@pytest_cases.fixture
def base_many_args(namespace):
    @use_fixture_namespace(namespace)
    class BaseTest:
        def test_example(self, arg_1, arg_2):
            return arg_1, arg_2

    return BaseTest


@pytest_cases.fixture
def base_one_arg_default(namespace):
    @use_fixture_namespace(namespace)
    class BaseTest:
        def test_example(self, default_arg=sentinel.DEFAULT_ARG):
            return default_arg

    return BaseTest


@pytest_cases.fixture
def base_many_args_default(namespace):
    @use_fixture_namespace(namespace)
    class BaseTest:
        def test_example(self, arg_1, default_arg_2=sentinel.DEFAULT_ARG_2):
            return arg_1, default_arg_2

    return BaseTest

#
#
# copy
# base_zero_args
#


@pytest_cases.fixture
def copy_zero_arg(namespace, base_zero_args):
    @use_fixture_namespace(namespace)
    class CopyTest:
        @func_copy(
            base_zero_args.test_example
        )
        def test_copy(self): pass

    return CopyTest


@pytest_cases.fixture
def copy_zero_arg_non_existing(namespace, base_zero_args):
    @use_fixture_namespace(namespace)
    class CopyTest:
        @func_copy(
            base_zero_args.test_example,
            map_args={'non_existing_arg': 'new_name'}
        )
        def test_copy(self): pass

    return CopyTest


@pytest_cases.fixture
def copy_zero_arg_self(namespace, base_zero_args):
    @use_fixture_namespace(namespace)
    class CopyTest:
        @func_copy(
            base_zero_args.test_example,
            map_args={'self': 'new_name'}
        )
        def test_copy(self): pass

    return CopyTest

#
#
# base_one_arg
#
#


@pytest_cases.fixture
def copy_one_arg(namespace, base_one_arg):
    @use_fixture_namespace(namespace)
    class CopyTest:
        @func_copy(
            base_one_arg.test_example
        )
        def test_copy(self): pass

    return CopyTest


@pytest_cases.fixture
def copy_one_arg_non_existing(namespace, base_one_arg):
    @use_fixture_namespace(namespace)
    class CopyTest:
        @func_copy(
            base_one_arg.test_example,
            map_args={'non_existing_arg': 'new_name'}
        )
        def test_copy(self): pass

    return CopyTest


@pytest_cases.fixture
def copy_one_arg_rename(namespace, base_one_arg):
    @use_fixture_namespace(namespace)
    class CopyTest:
        @func_copy(
            base_one_arg.test_example,
            map_args={'arg': 'new_name'}
        )
        def test_copy(self): pass

    return CopyTest


@pytest_cases.fixture
def copy_one_arg_self(namespace, base_one_arg):
    @use_fixture_namespace(namespace)
    class CopyTest:
        @func_copy(
            base_one_arg.test_example,
            map_args={'self': 'new_name'}
        )
        def test_copy(self): pass

    return CopyTest


@pytest_cases.fixture
def copy_one_arg_rename_default(namespace, base_one_arg_default):
    @use_fixture_namespace(namespace)
    class CopyTest:
        @func_copy(
            base_one_arg_default.test_example,
            map_args={'arg': 'new_name'}
        )
        def test_copy(self): pass

    return CopyTest

#
#
# base_many_args
#
#


@pytest_cases.fixture
def copy_many_args(namespace, base_many_args):
    @use_fixture_namespace(namespace)
    class CopyTest:
        @func_copy(
            base_many_args.test_example
        )
        def test_copy(self): pass

    return CopyTest


@pytest_cases.fixture
def copy_many_args_non_existing(namespace, base_many_args):
    @use_fixture_namespace(namespace)
    class CopyTest:
        @func_copy(
            base_many_args.test_example,
            map_args={'non_existing_arg': 'new_name'}
        )
        def test_copy(self): pass

    return CopyTest


@pytest_cases.fixture
def copy_many_args_self(namespace, base_many_args):
    @use_fixture_namespace(namespace)
    class CopyTest:
        @func_copy(
            base_many_args.test_example,
            map_args={'self': 'new_name'}
        )
        def test_copy(self): pass

    return CopyTest


@pytest_cases.fixture
def copy_many_args_rename(namespace, base_many_args):
    @use_fixture_namespace(namespace)
    class CopyTest:
        @func_copy(
            base_many_args.test_example,
            map_args={'arg_1': 'new_name_1', 'arg_2': 'new_name_2'}
        )
        def test_copy(self): pass

    return CopyTest


@pytest_cases.fixture
def copy_many_args_rename_default(namespace, base_many_args_default):
    @use_fixture_namespace(namespace)
    class CopyTest:
        @func_copy(
            base_many_args_default.test_example,
            map_args={'arg_1': 'new_name_1', 'arg_2': 'new_name_2'}
        )
        def test_copy(self): pass

    return CopyTest

#
#
# tests
#
#


@pytest_cases.parametrize('X, Y', [
    # empty default values
    (base_zero_args, copy_zero_arg),
    (base_one_arg, copy_one_arg),
    (base_many_args, copy_many_args),
    # default values
    (base_one_arg_default, copy_zero_arg),
    (base_many_args_default, copy_many_args)
])
def test_base_copy(X, Y):
    '''
    GIVEN class X with test_method_x
    AND class Y with test_method_y
    AND X.test_method_x can have default values
    WHEN using @func_copy with X.test_method_x
    THEN inject X.test_method_x code into Y.test_method_y method
    AND default values keep 
    '''
    pass


@pytest_cases.parametrize('X, Y', [
    # empty default values
    (base_one_arg, copy_one_arg_rename),
    (base_many_args, copy_many_args_rename),
    # default values
    (base_one_arg, copy_one_arg_rename_default),
    (base_many_args, copy_many_args_rename_default),
])
def test_copy_with_rename(X, Y):
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
    pass


@pytest_cases.parametrize('X, Y', [
    (base_zero_args, copy_zero_arg_self),
    (base_one_arg, copy_one_arg_self),
    (base_many_args, copy_many_args_self)
])
def test_copy_with_self_rename(X, Y):
    '''
    GIVEN class X with test_method_x
    AND class Y with test_method_y
    WHEN using @func_copy with X.test_method_x
    AND with renaming self argument
    THEN raise exception
    '''
    pass


@pytest_cases.parametrize('X, Y', [
    (base_one_arg, copy_zero_arg_non_existing),
    (base_one_arg, copy_one_arg_non_existing),
    (base_many_args, copy_many_args_non_existing)
])
def test_copy_with_non_existing_args_rename(X, Y):
    '''
    GIVEN class X with test_method_x
    AND class Y with test_method_y
    WHEN using @func_copy with X.test_method_x
    AND with renaming non existing arguments inside X.test_method_x
    THEN raise exception
    '''
    pass
