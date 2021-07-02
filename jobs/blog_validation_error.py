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

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

from jobs.types import base_validation_errors
import utils


class DuplicateBlogTitleError(base_validation_errors.BaseAuditError):
    """Error class for blog posts with duplicate titles."""

    def __init__(self, model):
        message = 'title=%s is not unique' % utils.quoted(model.title)
        super(DuplicateBlogTitleError, self).__init__(message, model)


class DuplicateBlogUrlError(base_validation_errors.BaseAuditError):
    """Error class for blog posts with duplicate urls."""

    def __init__(self, model):
        message = 'url=%s is not unique' % utils.quoted(model.title)
        super(DuplicateBlogTitleError, self).__init__(message, model)