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

"""Beam DoFns and PTransforms to provide validation of blog post models."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

import datetime

from core.platform import models
import feconf
from jobs import job_utils
from jobs.decorators import validation_decorators
from jobs.transforms import base_validation
from jobs.types import user_validation_errors

import apache_beam as beam
(base_models, blog_models) = models.Registry.import_models([
    models.NAMES.base_model, models.NAMES.blog])


@validation_decorators.AuditsExisting(
    blog_models.BlogPostModel,
    blog_models.BlogPostSummaryModel)
class ValidateBlogModelDomainObjectsInstances(
    base_validation.ValidateModelDomainObjectInstances):

    def _get_domain_object_validation_type(self, unused_item):
        """Returns the type of domain object validation to be performed.

        Args:
            unused_item: datastore_services.Model. Entity to validate.

        Returns:
            str. The type of validation mode: strict or non strict.
        """
        blog_post_rights = blog_services.get_blog_post_rights(
            item.id, strict=True)

        if blog_post_rights.blog_post_is_published:
            return VALIDATION_MODES.strict

        return VALIDATION_MODES.non_strict


@validation_decorators.AuditsExisting(blog_models.BlogPostModel)
class ValidateTitleMatchesSummaryModelTitle(beam.DoFn):
    """DoFn to validate that both blog post model title and summary model
    title are same."""

    def process(self, input_model):
        """Function that checks if the title of the model and the title of 
        corresponding summary model is unique.

        Args:
            input_model: BlogPostModel to validate.

        Yields:
            InvalidTitleError. Error for models with mismatch in title.
        """
        item = job_utils.clone_model(input_model)
        if item.title != '':
            blog_post_summary_title = (
                blog_models.BlogPostSummaryModel.get_by_id(item.id).title)
            if blog_post_summary_title != item.title:
                yield blog_validation_errors.ValidateTitleMatchesSummaryTitleError(
                    model)


@validation_decorators.RelationshipsOf(blog_models.BlogPostModel)
def blog_post_model_relationships(model):
    """Yields how the properties of the model relates to the ID of others."""
    yield model.id, [blog_models.BlogPostSummaryModel]
    yield model.id, [blog_models.BlogPostRightsModel]
    yield model.author_id, [user_models.UserSettingsModel]

@validation_decorators.RelationshipsOf(blog_models.BlogPostSummaryModel)
def blog_post_summary_model_relationships(model):
    """Yields how the properties of the model relates to the ID of others."""
    yield model.id, [blog_models.BlogPostModel]
    yield model.id, [blog_models.BlogPostRightsModel]
    yield model.author_id, [user_models.UserSettingsModel]

@validation_decorators.RelationshipsOf(blog_models.BlogPostRightsModel)
def blog_post_rights_model_relationships(model):
    """Yields how the properties of the model relates to the ID of others."""
    yield model.id, [blog_models.BlogPostModel]
    yield model.id, [blog_models.BlogPostSummaryModel]
    yield model.editor_ids, [user_models.UserSettingsModel]