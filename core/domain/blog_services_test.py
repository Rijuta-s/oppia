# coding: utf-8
#
# Copyright 2021 The Oppia Authors. All Rights Reserved.
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

"""Tests for blog post services."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

from core.domain import blog_domain
from core.domain import blog_services
from core.domain import user_services
from core.platform import models
from core.tests import test_utils

(blog_models,) = models.Registry.import_models([models.NAMES.blog])


class BlogServicesUnitTests(test_utils.GenericTestBase):
    """Tests for blog services."""

    def setUp(self):
        super(BlogServicesUnitTests, self).setUp()
        self.signup('a@example.com', 'A')
        self.signup('b@example.com', 'B')
        self.user_id_a = self.get_user_id_from_email('a@example.com')
        self.user_id_b = self.get_user_id_from_email('b@example.com')

        self.blog_post_a = blog_services.create_new_blog_post(self.user_id_a)
        self.blog_post_b = blog_services.create_new_blog_post(self.user_id_b)
        self.blog_post_a_id = self.blog_post_a.id
        self.blog_post_b_id = self.blog_post_b.id

        self.change_dict = {
            'tags': ['one', 'two']
        }
        self.change_dict_one = {
            'title': 'Sample Title',
            'thumbnail_filename': 'thummbnail.svg',
            'content': '<p>Hello</p>'
        }
        self.change_dict_two = {
            'title': 'Sample Title',
            'thumbnail_filename': 'thummbnail.svg',
            'content': '<p>Hello</p>',
            'tags': ['one', 'two']
        }

    def test_get_blog_post_from_model(self):
        blog_post_model = blog_models.BlogPostModel.get(self.blog_post_a_id)
        blog_post = blog_services.get_blog_post_from_model(blog_post_model)
        self.assertEqual(blog_post.to_dict(), self.blog_post_a.to_dict())

    def test_get_blog_post_by_id(self):
        expected_blog_post = self.blog_post_a.to_dict()
        blog_post = blog_services.get_blog_post_by_id(self.blog_post_a_id)
        self.assertEqual(blog_post.to_dict(), expected_blog_post)

    def test_get_blog_post_by_ids(self):
        blog_posts = blog_services.get_blog_post_by_ids([
            self.blog_post_a_id, self.blog_post_b_id])
        self.assertTrue(len(blog_posts) == 2)
        blog_post_ids = [blog_posts[0].id, blog_posts[1].id]
        self.assertTrue(self.blog_post_a_id in blog_post_ids)
        self.assertTrue(self.blog_post_b_id in blog_post_ids)

    def test_get_blog_post_summary_models_list_by_user_id(self):
        blog_posts = (
            blog_services.get_blog_post_summary_models_list_by_user_id(
                self.user_id_a, True))
        self.assertIsNone(blog_posts)
        blog_posts = (
            blog_services.get_blog_post_summary_models_list_by_user_id(
                self.user_id_a, False))
        self.assertEqual(self.blog_post_a_id, blog_posts[0].id)

    def test_get_new_blog_post_id(self):
        blog_post_id = blog_services.get_new_blog_post_id()
        self.assertFalse(blog_post_id == self.blog_post_a_id)
        self.assertFalse(blog_post_id == self.blog_post_b_id)

    def test_generate_summary_of_blog_post(self):
        html_content = '<a href="http://www.google.com">Hello, Oppia Blog</a>'
        expected_summary = 'Hello, Oppia Blog...'
        summary = blog_services.generate_summary_of_blog_post(html_content)
        self.assertEqual(expected_summary, summary)

        content = '<p>abc</p>' * 85
        expected_summary = 'abc' * 79 + '...'
        summary = blog_services.generate_summary_of_blog_post(content)
        self.assertEqual(expected_summary, summary)

    def test_compute_summary_of_blog_post(self):
        expected_blog_post_summary = (
            blog_domain.BlogPostSummary(
                self.blog_post_a_id,
                self.user_id_a,
                '',
                '...',
                '',
                [],
            )
        )
        blog_post_summary = (
            blog_services.compute_summary_of_blog_post(self.blog_post_a))
        self.assertEqual(
            expected_blog_post_summary.to_dict(), blog_post_summary.to_dict())

    def test_get_blog_post_summary_from_model(self):
        blog_post_summary_model = (
            blog_models.BlogPostSummaryModel.get(self.blog_post_a_id))
        blog_post_summary = (
            blog_services.get_blog_post_summary_from_model(
                blog_post_summary_model))
        expected_blog_post_summary = (
            blog_domain.BlogPostSummary(
                self.blog_post_a_id,
                self.user_id_a,
                '',
                '...',
                '',
                [],
            )
        )
        self.assertEqual(
            blog_post_summary.to_dict(), expected_blog_post_summary.to_dict())

    def test_blog_post_summary_by_id(self):
        blog_post_summary = (
            blog_services.get_blog_post_summary_by_id(
                self.blog_post_a_id, strict=True))
        expected_blog_post_summary = (
            blog_domain.BlogPostSummary(
                self.blog_post_a_id,
                self.user_id_a,
                '',
                '...',
                '',
                [],
            )
        )
        self.assertEqual(
            blog_post_summary.to_dict(), expected_blog_post_summary.to_dict())

    def test_publish_blog_post(self):
        blog_post_rights = (
            blog_services.get_blog_post_rights(self.blog_post_a_id))
        self.assertFalse(blog_post_rights.blog_post_is_published)

        blog_services.update_blog_post(
            self.blog_post_a_id, self.change_dict_two)
        blog_services.publish_blog_post(self.blog_post_a_id)
        blog_post_summary = (
            blog_services.get_blog_post_summary_by_id(self.blog_post_a_id))
        blog_post = blog_services.get_blog_post_by_id(self.blog_post_a_id)
        blog_post_rights = (
            blog_services.get_blog_post_rights(self.blog_post_a_id))

        self.assertTrue(blog_post_rights.blog_post_is_published)
        self.assertIsNotNone(blog_post.published_on)
        self.assertIsNotNone(blog_post_summary.published_on)
        self.assertEqual(
            blog_post.published_on, blog_post_summary.published_on)

    def test_cannot_publish_invalid_blog_post(self):
        """Checks that an invalid blog post is not published."""
        with self.assertRaisesRegexp(
            Exception, ('Title should not be empty')):
            blog_services.publish_blog_post(self.blog_post_a_id)

        blog_services.update_blog_post(
            self.blog_post_a_id, self.change_dict_one)
        with self.assertRaisesRegexp(
            Exception, ('Atleast one tag should be selected')):
            blog_services.publish_blog_post(self.blog_post_a_id)

        change_dict_three = {
            'title': 'Sample Title',
            'thumbnail_filename': 'thummbnail.svg',
            'content': '',
            'tags': ['one', 'two']
        }

        blog_services.update_blog_post(self.blog_post_a_id, change_dict_three)
        with self.assertRaisesRegexp(
            Exception, ('Content can not be empty')):
            blog_services.publish_blog_post(self.blog_post_a_id)

    def test_unpublish_blog_post(self):
        blog_services.update_blog_post(
            self.blog_post_a_id, self.change_dict_two)
        blog_services.publish_blog_post(self.blog_post_a_id)
        blog_post_rights = (
            blog_services.get_blog_post_rights(self.blog_post_a_id))
        self.assertTrue(blog_post_rights.blog_post_is_published)

        blog_services.unpublish_blog_post(self.blog_post_a_id)
        blog_post_rights = (
            blog_services.get_blog_post_rights(self.blog_post_a_id))
        self.assertFalse(blog_post_rights.blog_post_is_published)

    def test_filter_blog_post_ids(self):
        blog_services.update_blog_post(
            self.blog_post_a_id, self.change_dict_two)
        blog_services.publish_blog_post(self.blog_post_a_id)
        filtered_model_ids = (
            blog_services.filter_blog_post_ids(self.user_id_a, True))
        self.assertEqual(filtered_model_ids, [self.blog_post_a_id])
        filtered_model_ids = (
            blog_services.filter_blog_post_ids(self.user_id_b, False))
        self.assertEqual(filtered_model_ids, [self.blog_post_b_id])

    def test_get_all_blog_posts(self):
        blog_posts = blog_services.get_all_blog_posts()
        self.assertEqual(len(blog_posts), 2)
        blog_post_ids = [blog_posts[0].id, blog_posts[1].id]
        self.assertTrue(self.blog_post_a_id in blog_post_ids)

    def test_update_blog_post(self):
        self.assertEqual(self.blog_post_a.title, '')
        blog_services.update_blog_post(
            self.blog_post_a_id, self.change_dict_one)
        updated_blog_post = (
            blog_services.get_blog_post_by_id(self.blog_post_a_id))
        self.assertEqual(updated_blog_post.thumbnail_filename, 'thummbnail.svg')
        self.assertEqual(updated_blog_post.content, '<p>Hello</p>')
        self.assertEqual(updated_blog_post.url_fragment, 'sample-title')

        blog_services.update_blog_post(self.blog_post_a_id, self.change_dict)
        updated_blog_post = (
            blog_services.get_blog_post_by_id(self.blog_post_a_id))
        self.assertEqual(updated_blog_post.tags, ['one', 'two'])

        with self.assertRaisesRegexp(
            Exception, (
                'Blog Post with given title already exists: %s'
                % 'Sample Title')):
            blog_services.update_blog_post(
                self.blog_post_b_id, self.change_dict_one)

    def test_get_blog_post_by_url_fragment(self):
        blog_services.update_blog_post(
            self.blog_post_a_id, self.change_dict_one)
        expected_blog_post = (
            blog_services.get_blog_post_by_id(self.blog_post_a_id))
        blog_post = blog_services.get_blog_post_by_url_fragment('sample-title')
        self.assertEqual(blog_post.to_dict(), expected_blog_post.to_dict())

    def test_does_blog_post_with_url_fragment_exist(self):
        blog_services.update_blog_post(
            self.blog_post_a_id, self.change_dict_one)
        self.assertTrue(
            blog_services.does_blog_post_with_url_fragment_exist(
                'sample-title'))
        self.assertFalse(
            blog_services.does_blog_post_with_url_fragment_exist('title'))

    def test_update_blog_post_summary(self):
        blog_post_summary = (
            blog_services.get_blog_post_summary_by_id(
                self.blog_post_a_id, strict=True))
        self.assertEqual(blog_post_summary.title, '')
        blog_services.update_blog_post(
            self.blog_post_a_id, self.change_dict_one)
        updated_blog_post_summary = (
            blog_services.get_blog_post_summary_by_id(
                self.blog_post_a_id, strict=True))
        self.assertEqual(
            updated_blog_post_summary.thumbnail_filename, 'thummbnail.svg')
        self.assertEqual(updated_blog_post_summary.summary, 'Hello...')
        self.assertEqual(updated_blog_post_summary.url_fragment, 'sample-title')

    def test_check_can_edit_blog_post(self):
        blog_post_rights = (
            blog_services.get_blog_post_rights(self.blog_post_a_id))
        user_info_a = user_services.get_user_actions_info(self.user_id_a)
        user_info_b = user_services.get_user_actions_info(self.user_id_b)
        self.assertFalse(blog_services.check_can_edit_blog_post(
            user_info_b, blog_post_rights))
        self.assertTrue(blog_services.check_can_edit_blog_post(
            user_info_a, blog_post_rights))

    def test_deassign_user_from_all_blog_posts(self):
        blog_post_rights = (
            blog_services.get_blog_post_rights(self.blog_post_a_id))
        self.assertTrue(self.user_id_a in blog_post_rights.editor_ids)

        blog_services.deassign_user_from_all_blog_posts(self.user_id_a)

        updated_blog_post_rights = (
            blog_services.get_blog_post_rights(self.blog_post_a_id))
        self.assertFalse(self.user_id_a in updated_blog_post_rights.editor_ids)

    def test_generate_url_fragment(self):
        url_fragment = (
            blog_services.generate_url_fragment('Sample Url Fragment'))
        self.assertEqual(url_fragment, 'sample-url-fragment')

        url_fragment = (
            blog_services.generate_url_fragment('SaMple Url FrAgMent'))
        self.assertEqual(url_fragment, 'sample-url-fragment')

    def test_save_blog_post_rights(self):
        blog_post_rights = blog_domain.BlogPostRights(
            self.blog_post_a_id,
            [self.user_id_a, self.user_id_b],
            False
        )
        blog_services.save_blog_post_rights(blog_post_rights)
        fetched_blog_post_rights = (
            blog_services.get_blog_post_rights(self.blog_post_a_id))
        self.assertEqual(
            blog_post_rights.to_dict(), fetched_blog_post_rights.to_dict())

    def test_delete_blog_post(self):
        blog_services.delete_blog_post(self.blog_post_a_id)
        self.assertIsNone(blog_services.get_blog_post_rights(
            self.blog_post_a_id, strict=False))
        self.assertIsNone(blog_services.get_blog_post_by_id(
            self.blog_post_a_id, strict=False))
        self.assertIsNone(blog_services.get_blog_post_summary_by_id(
            self.blog_post_a_id, strict=False))

    def test_get_blog_post_summary_by_title(self):
        model = (
            blog_models.BlogPostSummaryModel.get_by_id(self.blog_post_a_id))
        model.title = 'Hello Bloggers'
        model.update_timestamps()
        model.put()

        blog_post_summary = (
            blog_services.get_blog_post_summary_by_id(
                self.blog_post_a_id, strict=True))
        expected_blog_post_summary = (
            blog_domain.BlogPostSummary(
                self.blog_post_a_id,
                self.user_id_a,
                'Hello Bloggers',
                '...',
                '',
                [],
            )
        )
        self.assertEqual(
            blog_post_summary.to_dict(), expected_blog_post_summary.to_dict())
