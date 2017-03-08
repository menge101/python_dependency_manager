import inspect
from six import iteritems
import sys


class DependencyManager(object):
    """
    This handles runtime dependency wrangling.
    Because the CLI allows an end user to specify what class to use for various components of the system at run-time,
    none of these dependencies are hard-coded into the system.
    This class expects generators to be in the 'generators' folder and writers to bein 'writers',
    but beyond that anything the user wants to put in those folders ... and add to the __init__.py ...
    is available to be used in the system.

    There is the beginnings of an aliasing system so you don't need to refer to classes by their full name,
    but that hasn't been maintained.  It will hopefully be restored.
    """
    # TODO: Find a way to automatically import all classes into a module.
    # TODO: Also have the dependency manager handle if that fails

    _alias_map = {'class_creators': {'tse': 'TseClassCreator', 'generic': 'ClassCreator'},
                  'generators': {'tse': 'TseLoadGenerator'}, 'writers': {'transaction': 'TransactionWriter'}}

    def __init__(self, dependency, alias_map=_alias_map):
        if not self._check_dependency_type(dependency):
            self.import_module(dependency)
        self.module_name = dependency
        try:
            self.aliases = alias_map[self.module_name]
        except KeyError:
            self.aliases = dict()
        self.valid_dependency_list = [item[0] for item in
                                      inspect.getmembers(sys.modules[dependency], inspect.isclass)]

    def get_class(self, dependency_string):
        if self.valid(dependency_string):
            return getattr(sys.modules[self.module_name], self.normalize(dependency_string))
        else:
            raise TypeError("{} is not a valid {} object".format(dependency_string, self.module_name))

    def list_options(self):
        valid_normalization_list = self.list_normalizations(self.aliases, self.valid_dependency_list)
        full_valid_list = valid_normalization_list + self.valid_dependency_list
        full_valid_list.sort()
        return full_valid_list

    def normalize(self, string):
        try:
            return self.aliases[string]
        except KeyError:
            return string

    def valid(self, generator_string):
        normalized_string = self.normalize(generator_string)
        return normalized_string in self.valid_dependency_list

    @classmethod
    def get_class_from_module(cls, class_name, module):
        if module not in sys.modules:
            cls.import_module(module)
        return getattr(sys.modules[module], class_name)

    @classmethod
    def import_module(cls, module_name):
        __import__(module_name)

    @staticmethod
    def list_normalizations(normalization_dict, valid_dependency_list):
        try:
            return [item for item in normalization_dict.keys() if normalization_dict[item] in valid_dependency_list]
        except KeyError:
            return list()

    @classmethod
    def list_valid_types(cls):
        return cls._compact_dict(sys.modules).keys()

    @classmethod
    def obtain_module(cls, module_name):
        compacted_module_list = cls._compact_dict(sys.modules)
        try:
            module = compacted_module_list[module_name]
        except KeyError:
            cls.import_module(module_name)
            module = sys.modules[module_name]
        return module

    @classmethod
    def _check_dependency_type(cls, dep_type):
        valid_types = cls.list_valid_types()
        return dep_type in valid_types

    @staticmethod
    def _compact_dict(dikt):
        return dict((k, v) for k, v in iteritems(dikt) if v)
