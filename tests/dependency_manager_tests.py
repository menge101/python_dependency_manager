from dependency_manager import DependencyManager
import sys
import unittest


class DependencyValidatorTests(unittest.TestCase):
    def test_validate(self):
        self.writer_validate = DependencyManager('writers')
        self.generator_validator = DependencyManager('generators')
        self.assertTrue(self.generator_validator.valid('tse'))
        self.assertFalse(self.generator_validator.valid('abc'))
        self.assertTrue(self.writer_validate.valid('transaction'))
        self.assertFalse(self.writer_validate.valid('json'))

    def test_normalize(self):
        self.writer_validate = DependencyManager('writers')
        self.generator_validator = DependencyManager('generators')
        self.assertEqual('TseLoadGenerator', self.generator_validator.normalize('tse'))
        self.assertEqual('abc', self.generator_validator.normalize('abc'))
        self.assertEqual('TransactionWriter', self.writer_validate.normalize('transaction'))
        self.assertEqual('json', self.writer_validate.normalize('json'))

    def test_raises_on_import_error(self):
        fake_module = 'ninjas'
        try:
            DependencyManager(fake_module)
        except ImportError as ie:
            self.assertEqual('No module named {}'.format(fake_module), ie.message)
        else:
            self.assertTrue(False)

    def test_list_valid_types(self):
        valid_types = DependencyManager.list_valid_types()
        self.assertIn('unittest', valid_types)
        self.assertNotIn('robots', valid_types)

    def test_list_options(self):
        writer_validate = DependencyManager('writers')
        generator_validator = DependencyManager('generators')
        self.assertItemsEqual(
            ['AbstractGenerator', 'DebugGenerator', 'SignalCheckLoadGenerator', 'TseLoadGenerator', 'tse'],
            generator_validator.list_options())
        self.assertItemsEqual(['AbstractWriter', 'transaction', 'TransactionWriter', 'Executor'],
                              writer_validate.list_options())

    def test_valid_get(self):
        wv = DependencyManager('writers')
        klass = wv.get_class('transaction')
        class_type = klass.__name__
        self.assertEqual('TransactionWriter', class_type)

    def test_invalid_get(self):
        wv = DependencyManager('writers')
        try:
            wv.get_class('ninjas')
        except TypeError as te:
            self.assertEqual('ninjas is not a valid writers object', te.message)
        else:
            self.assertTrue(False)

    def test_obtain_module_already_imported(self):
        module_name = DependencyManager._compact_dict(sys.modules).keys()[7]
        DependencyManager.obtain_module(module_name)
        self.assertIn(module_name, sys.modules)

    def test_obtain_module_not_imported(self):
        module_name = 'mocks'
        if module_name in sys.modules:
            del(sys.modules[module_name])
        self.assertNotIn(module_name, sys.modules)
        DependencyManager.obtain_module(module_name)
        self.assertIn(module_name, sys.modules)

    def test_get_class_from_module(self):
        klass = DependencyManager.get_class_from_module('TransactionWriter', 'writers')
        class_type = klass.__name__
        self.assertEqual('TransactionWriter', class_type)

    def test_get_class_from_module_not_loaded(self):
        module_name = 'mocks'
        if module_name in sys.modules:
            del (sys.modules[module_name])
        self.assertNotIn(module_name, sys.modules)
        klass = DependencyManager.get_class_from_module('WriterMock', module_name)
        class_type = klass.__name__
        self.assertEqual('WriterMock', class_type)

    def test_get_class_from_module_not_real_class(self):
        module_name = 'mocks'
        if module_name in sys.modules:
            del (sys.modules[module_name])
        self.assertNotIn(module_name, sys.modules)
        try:
            DependencyManager.get_class_from_module('Ninja', module_name)
        except AttributeError as ae:
            self.assertEqual("'module' object has no attribute 'Ninja'", ae.message)
        else:
            self.assertTrue(False)

    def test_get_class_from_module_not_real_module(self):
        try:
            DependencyManager.get_class_from_module('Hayabusa', 'ninjas')
        except ImportError as ie:
            self.assertEqual('No module named ninjas', ie.message)
        else:
            self.assertTrue(False)
