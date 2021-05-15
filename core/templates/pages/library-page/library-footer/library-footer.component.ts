// Copyright 2019 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Directive for the library footer.
 */
 import { Component, OnInit } from '@angular/core';
 import { downgradeComponent } from '@angular/upgrade/static';
 import { LibraryPageConstants } from 'pages/library-page/library-page.constants';
 import { WindowRef } from 'services/contextual/window-ref.service';

 @Component({
  selector: 'library-footer',
  templateUrl: './library-footer.component.html'
})
export class LibraryFooterComponent implements OnInit {
  footerIsDisplayed: boolean;
  constructor(
    private windowRef: WindowRef,
  ) {}

  ngOnInit(): void {
    var pageMode = LibraryPageConstants.LIBRARY_PATHS_TO_MODES[
      this.windowRef.nativeWindow.location.pathname];
    this.footerIsDisplayed = (pageMode !== LibraryPageConstants.LIBRARY_PAGE_MODES.SEARCH);
  };
}

angular.module('oppia').directive(
  'libraryFooter', downgradeComponent({component: LibraryFooterComponent}));