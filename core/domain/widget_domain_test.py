# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Jeremy Emerson'

import os
import re
import string

from core.domain import dependency_registry
from core.domain import obj_services
from core.domain import widget_domain
from core.domain import widget_registry
from core.tests import test_utils
import feconf
import schema_utils
import schema_utils_test
import utils


class AnswerHandlerUnitTests(test_utils.GenericTestBase):
    """Test the AnswerHandler domain object."""

    def test_rules_property(self):
        """Test that answer_handler.rules behaves as expected."""
        answer_handler = widget_domain.AnswerHandler('submit', 'Null')
        self.assertEqual(answer_handler.name, 'submit')
        self.assertEqual(answer_handler.rules, [])

        answer_handler = widget_domain.AnswerHandler(
            'submit', 'NonnegativeInt')
        self.assertEqual(len(answer_handler.rules), 1)

        with self.assertRaisesRegexp(Exception, 'not a valid object class'):
            widget_domain.AnswerHandler('submit', 'FakeObjType')


class WidgetUnitTests(test_utils.GenericTestBase):
    """Test the widget domain object and registry."""

    def test_parameterized_widget(self):
        """Test that parameterized widgets are correctly handled."""

        TEXT_INPUT_ID = 'TextInput'

        widget = widget_registry.Registry.get_widget_by_id(
            feconf.INTERACTIVE_PREFIX, TEXT_INPUT_ID)
        self.assertEqual(widget.id, TEXT_INPUT_ID)
        self.assertEqual(widget.name, 'Text input')

        self.assertIn('input ng-if="rows == 1"', widget.html_body)

        tag = widget.get_interactive_widget_tag({})
        self.assertEqual(
            '<oppia-interactive-text-input '
            'placeholder-with-value="&#34;Type your answer here.&#34;" '
            'rows-with-value="1">'
            '</oppia-interactive-text-input>', tag)

        tag = widget.get_interactive_widget_tag({
            'placeholder': {'value': 'F4'}
        })
        self.assertEqual(
            '<oppia-interactive-text-input '
            'placeholder-with-value="&#34;F4&#34;" rows-with-value="1">'
            '</oppia-interactive-text-input>', tag)

        parameterized_widget_dict = widget.get_widget_instance_dict(
            {'placeholder': 'F4'})
        self.assertItemsEqual(parameterized_widget_dict.keys(), [
            'widget_id', 'name', 'category', 'description',
            'handler_specs', 'customization_args', 'tag'])
        self.assertEqual(
            parameterized_widget_dict['widget_id'], TEXT_INPUT_ID)

        self.assertEqual([{
            'name': 'placeholder',
            'value': 'F4',
            'description': 'The placeholder for the text input field.',
            'schema': {'type': 'unicode'},
            'custom_editor': None,
            'default_value': 'Type your answer here.',
        }, {
            'name': 'rows',
            'value': 1,
            'description': 'The number of rows for the text input field.',
            'schema': {
                'type': 'int',
                'post_normalizers': [{
                    'id': 'require_at_least', 'min_value': 1
                }, {
                    'id': 'require_at_most', 'max_value': 200
                }]
            },
            'custom_editor': None,
            'default_value': 1,
        }], parameterized_widget_dict['customization_args'])


class WidgetDataUnitTests(test_utils.GenericTestBase):
    """Tests that all the default widgets are valid."""

    def _is_camel_cased(self, name):
        """Check whether a name is in CamelCase."""
        return name and (name[0] in string.ascii_uppercase)

    def _is_alphanumeric_string(self, string):
        """Check whether a string is alphanumeric."""
        return bool(re.compile("^[a-zA-Z0-9_]+$").match(string))

    def test_allowed_widgets(self):
        """Do sanity checks on the ALLOWED_WIDGETS dict in feconf.py."""
        widget_registries = [
            feconf.ALLOWED_WIDGETS[feconf.NONINTERACTIVE_PREFIX],
            feconf.ALLOWED_WIDGETS[feconf.INTERACTIVE_PREFIX]
        ]

        for registry in widget_registries:
            for (widget_name, definition) in registry.iteritems():
                contents = os.listdir(
                    os.path.join(os.getcwd(), definition['dir']))
                self.assertIn('%s.py' % widget_name, contents)

    def test_widget_counts(self):
        """Test that the correct number of widgets are loaded."""
        widget_registry.Registry.refresh()

        self.assertEqual(
            len(widget_registry.Registry.interactive_widgets),
            len(feconf.ALLOWED_WIDGETS[feconf.INTERACTIVE_PREFIX])
        )
        self.assertEqual(
            len(widget_registry.Registry.noninteractive_widgets),
            len(feconf.ALLOWED_WIDGETS[feconf.NONINTERACTIVE_PREFIX])
        )

    def test_image_data_urls_for_noninteractive_widgets(self):
        """Test the data urls for the noninteractive widget editor icons."""
        widget_registry.Registry.refresh()

        widget_list = widget_registry.Registry.noninteractive_widgets
        allowed_widgets = feconf.ALLOWED_WIDGETS[feconf.NONINTERACTIVE_PREFIX]
        for widget_name in allowed_widgets:
            image_filepath = os.path.join(
                os.getcwd(), allowed_widgets[widget_name]['dir'],
                '%s.png' % widget_name)
            self.assertEqual(
                utils.convert_png_to_data_url(image_filepath),
                widget_list[widget_name].icon_data_url
            )

    def test_default_widgets_are_valid(self):
        """Test the default widgets."""
        bindings = widget_registry.Registry.interactive_widgets

        # TODO(sll): These tests ought to include non-interactive widgets as
        # well.

        for widget_id in feconf.ALLOWED_WIDGETS[feconf.INTERACTIVE_PREFIX]:
            # Check that the widget_id name is valid.
            self.assertTrue(self._is_camel_cased(widget_id))

            # Check that the widget directory exists.
            widget_dir = os.path.join(
                feconf.INTERACTIVE_WIDGETS_DIR, widget_id)
            self.assertTrue(os.path.isdir(widget_dir))

            # In this directory there should only be a config .py file, an
            # html file, a JS file, (optionally) a directory named 'static',
            # (optionally) a widget JS test file, and (optionally) a
            # stats_response.html file.
            dir_contents = os.listdir(widget_dir)
            self.assertLessEqual(len(dir_contents), 7)

            optional_dirs_and_files_count = 0

            try:
                self.assertIn('static', dir_contents)
                static_dir = os.path.join(widget_dir, 'static')
                self.assertTrue(os.path.isdir(static_dir))
                optional_dirs_and_files_count += 1
            except Exception:
                pass

            try:
                self.assertTrue(os.path.isfile(
                    os.path.join(widget_dir, 'stats_response.html')))
                optional_dirs_and_files_count += 1
            except Exception:
                pass

            try:
                self.assertTrue(os.path.isfile(os.path.join(
                    widget_dir, '%s.pyc' % widget_id)))
                optional_dirs_and_files_count += 1
            except Exception:
                pass

            try:
                self.assertTrue(os.path.isfile(os.path.join(
                    widget_dir, '%sSpec.js' % widget_id)))
                optional_dirs_and_files_count += 1
            except Exception:
                pass

            self.assertEqual(
                optional_dirs_and_files_count + 3, len(dir_contents),
                dir_contents
            )

            py_file = os.path.join(widget_dir, '%s.py' % widget_id)
            html_file = os.path.join(widget_dir, '%s.html' % widget_id)
            js_file = os.path.join(widget_dir, '%s.js' % widget_id)

            self.assertTrue(os.path.isfile(py_file))
            self.assertTrue(os.path.isfile(html_file))
            self.assertTrue(os.path.isfile(js_file))

            js_file_content = utils.get_file_contents(js_file)
            html_file_content = utils.get_file_contents(html_file)
            self.assertIn('oppiaInteractive%s' % widget_id, js_file_content)
            self.assertIn('oppiaResponse%s' % widget_id, js_file_content)
            self.assertIn(
                '<script type="text/ng-template" '
                'id="interactiveWidget/%s"' % widget_id,
                html_file_content)
            self.assertIn(
                '<script type="text/ng-template" id="response/%s"' % widget_id,
                html_file_content)
            self.assertNotIn('<script>', js_file_content)
            self.assertNotIn('</script>', js_file_content)

            WIDGET_CONFIG_SCHEMA = [
                ('name', basestring), ('category', basestring),
                ('description', basestring), ('_handlers', list),
                ('_customization_arg_specs', list)
            ]

            widget = bindings[widget_id]

            # Check that the specified widget id is the same as the class name.
            self.assertTrue(widget_id, widget.__class__.__name__)

            # Check that the configuration file contains the correct
            # top-level keys, and that these keys have the correct types.
            for item, item_type in WIDGET_CONFIG_SCHEMA:
                self.assertTrue(isinstance(
                    getattr(widget, item), item_type
                ))
                # The string attributes should be non-empty.
                if item_type == basestring:
                    self.assertTrue(getattr(widget, item))

            # Check that at least one handler exists.
            self.assertTrue(
                len(widget.handlers),
                msg='Widget %s has no handlers defined' % widget_id
            )

            for handler in widget._handlers:
                HANDLER_KEYS = ['name', 'obj_type']
                self.assertItemsEqual(HANDLER_KEYS, handler.keys())
                self.assertTrue(isinstance(handler['name'], basestring))
                # Check that the obj_type corresponds to a valid object class.
                obj_services.Registry.get_object_class_by_type(
                    handler['obj_type'])

            # Check that all handler names are unique.
            names = [handler.name for handler in widget.handlers]
            self.assertEqual(
                len(set(names)),
                len(names),
                'Widget %s has duplicate handler names' % widget_id
            )

            for ca_spec in widget._customization_arg_specs:
                CA_SPEC_KEYS = ['name', 'description', 'default_value',
                                'schema', 'custom_editor']
                for key in ca_spec:
                    self.assertIn(key, CA_SPEC_KEYS)

                self.assertTrue(isinstance(ca_spec['name'], basestring))
                self.assertTrue(self._is_alphanumeric_string(ca_spec['name']))
                self.assertTrue(isinstance(ca_spec['description'], basestring))
                self.assertGreater(len(ca_spec['description']), 0)

                # Exactly one of 'schema' or 'custom_editor' should be present.
                self.assertTrue(
                    'schema' in ca_spec or 'custom_editor' in ca_spec)
                self.assertFalse(
                    'schema' in ca_spec and 'custom_editor' in ca_spec)

                if 'schema' in ca_spec:
                    schema_utils_test.validate_schema(ca_spec['schema'])
                    self.assertEqual(
                        ca_spec['default_value'],
                        schema_utils.normalize_against_schema(
                            ca_spec['default_value'], ca_spec['schema']))
                else:
                    obj_class = obj_services.Registry.get_object_class_by_type(
                        ca_spec['custom_editor'])
                    self.assertIsNotNone(obj_class.edit_html_filename)
                    self.assertIsNotNone(obj_class.edit_js_filename)
                    self.assertEqual(
                        ca_spec['default_value'],
                        obj_class.normalize(ca_spec['default_value']))

            # Check that all dependency ids are valid.
            for dependency_id in widget.dependency_ids:
                dependency_registry.Registry.get_dependency_html(dependency_id)
