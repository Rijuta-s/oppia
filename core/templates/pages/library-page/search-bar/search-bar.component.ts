// Copyright 2016 The Oppia Authors. All Rights Reserved.
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
 * @fileoverview Component for the Search Bar.
 */

import { Subscription } from 'rxjs';
import constants from 'assets/constants';
import { NavigationService } from 'services/navigation.service';
import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { downgradeComponent } from '@angular/upgrade/static';
import { ClassroomBackendApiService } from 'domain/classroom/classroom-backend-api.service';
import { I18nLanguageCodeService } from 'services/i18n-language-code.service';
import { SearchService } from 'services/search.service';
import { UrlInterpolationService } from 'domain/utilities/url-interpolation.service';
import { WindowDimensionsService } from 'services/contextual/window-dimensions.service';
import { WindowRef } from 'services/contextual/window-ref.service';
import { UrlService } from 'services/contextual/url.service';
import { TranslateService } from 'services/translate.service'
import { ConstructTranslationIdsService } from 'services/construct-translation-ids.service';
import { LanguageUtilService } from 'domain/utilities/language-util.service';

interface SearchDropDownCategories {
  id: string;
  text: string;
}

interface LanguageIdAndText {
  id: string;
  text: string;
}

interface SelectionDetails {
  categories: {
    description: string,
    itemsName: string,
    masterList: SearchDropDownCategories[],
    numSelections: number,
    selections: {},
    summary: string,
  },
  languageCodes: {
    description: string,
    itemsName: string,
    masterList: LanguageIdAndText[],
    numSelections: number,
    selections: {},
    summary: string,
  }
}
@Component({
  selector: 'search-bar',
  templateUrl: './search-bar.component.html'
})

export class SearchBarComponent implements OnInit, OnDestroy {
  @Input() enableDropup: boolean;
  directiveSubscriptions: Subscription = new Subscription();
  SEARCH_DROPDOWN_CATEGORIES: SearchDropDownCategories[];
  ACTION_OPEN: string;
  ACTION_CLOSE: string
  KEYBOARD_EVENT_TO_KEY_CODES: {};
  searchQuery: string = '';
  classroomPageIsActive: boolean;
  SUPPORTED_CONTENT_LANGUAGES: LanguageIdAndText[];
  selectionDetails: SelectionDetails
  translationData = {};
  activeMenuName: string;
  searchBarPlaceholder: string;
  categoryButtonText: string;
  languageButtonText: string;
  constructor(
    private i18nLanguageCodeService: I18nLanguageCodeService,
    private windowRef: WindowRef,
    private searchService: SearchService,
    private urlService: UrlService,
    private windowDimensionsService: WindowDimensionsService,
    private navigationService: NavigationService,
    private classroomBackendApiService: ClassroomBackendApiService,
    private languageUtilService: LanguageUtilService,
    private constructTranslationIdsService: ConstructTranslationIdsService,
    private translateService : TranslateService
  ){}
  
  ngOnInit() {
    this.classroomPageIsActive = (
      this.urlService.getPathname().startsWith('/learn'));
    this.SEARCH_DROPDOWN_CATEGORIES = (
      constants.SEARCH_DROPDOWN_CATEGORIES.map((categoryName) => {
          return {
            id: categoryName,
            text: this.constructTranslationIdsService.getLibraryId(
              'categories', categoryName)
          };
        }
      )
    );
    this.ACTION_OPEN = this.navigationService.ACTION_OPEN;
    this.ACTION_CLOSE = this.navigationService.ACTION_CLOSE;
    this.KEYBOARD_EVENT_TO_KEY_CODES =
    this.navigationService.KEYBOARD_EVENT_TO_KEY_CODES;
    this.SUPPORTED_CONTENT_LANGUAGES = (
      this.languageUtilService.getLanguageIdsAndTexts());
    this.selectionDetails = {
      categories: {
        description: '',
        itemsName: 'categories',
        masterList: this.SEARCH_DROPDOWN_CATEGORIES,
        numSelections: 0,
        selections: {},
        summary: ''
      },
      languageCodes: {
        description: '',
        itemsName: 'languages',
        masterList: this.SUPPORTED_CONTENT_LANGUAGES,
        numSelections: 0,
        selections: {},
        summary: ''
      }
    };

    // Non-translatable parts of the html strings, like numbers or user
    // names.
    this.translationData = {};
    // Initialize the selection descriptions and summaries.
    for (var itemsType in this.selectionDetails) {
      this.updateSelectionDetails(itemsType);
    }
    // $scope.$on('$locationChangeSuccess', () => {
    //   if (this.urlService.getUrlParams().hasOwnProperty('q')) {
    //    this.updateSearchFieldsBasedOnUrlQuery();
    //   }
    // });

    this.directiveSubscriptions.add(
      this.i18nLanguageCodeService.onPreferredLanguageCodesLoaded.subscribe(
        (preferredLanguageCodesList) => {
          preferredLanguageCodesList.forEach((languageCode) => {
            var selections =
            this.selectionDetails.languageCodes.selections;
            if (!selections.hasOwnProperty(languageCode)) {
              selections[languageCode] = true;
            } else {
              selections[languageCode] = !selections[languageCode];
            }
          });

          this.updateSelectionDetails('languageCodes');

          if (this.urlService.getUrlParams().hasOwnProperty('q')) {
            this.updateSearchFieldsBasedOnUrlQuery();
          }

          if (this.windowRef.nativeWindow.location.pathname === '/search/find') {
            this.onSearchQueryChangeExec();
          }

          this.refreshSearchBarLabels();

          // Notify the function that handles overflow in case the
          // search elements load after it has already been run.
          this.searchService.onSearchBarLoaded.emit();
        }
      )
    );
    this.directiveSubscriptions.add(
      this.translateService.onLangChange
        .subscribe(() => this.refreshSearchBarLabels()));

    this.directiveSubscriptions.add(
      this.classroomBackendApiService.onInitializeTranslation
        .subscribe(() => this.refreshSearchBarLabels()));
  };

  refreshSearchBarLabels(): void {
    // If you translate these strings in the html, then you must use a
    // filter because only the first 14 characters are displayed. That
    // would generate FOUC for languages other than English. As an
    // exception, we translate them here and update the translation
    // every time the language is changed.
    this.searchBarPlaceholder = this.translateService.getInterpolatedString(
      'I18N_LIBRARY_SEARCH_PLACEHOLDER');
    // 'messageformat' is the interpolation method for plural forms.
    // http://angular-translate.github.io/docs/#/guide/14_pluralization.
    this.categoryButtonText = this.translateService.getInterpolatedString(
      this.selectionDetails.categories.summary,
      this.translationData);
      // , 'messageformat'
    this.languageButtonText = this.translateService.getInterpolatedString(
      this.selectionDetails.languageCodes.summary,
      this.translationData);
  };

  // Update the description, numSelections and summary fields of the
  // relevant entry of this.selectionDetails.
  updateSelectionDetails(itemsType): void {
    var itemsName = this.selectionDetails[itemsType].itemsName;
    var masterList = this.selectionDetails[itemsType].masterList;

    var selectedItems = [];
    for (var i = 0; i < masterList.length; i++) {
      if (this.selectionDetails[itemsType]
        .selections[masterList[i].id]) {
        selectedItems.push(masterList[i].text);
      }
    }

    var totalCount = selectedItems.length;
    this.selectionDetails[itemsType].numSelections = totalCount;

    this.selectionDetails[itemsType].summary = (
      totalCount === 0 ? 'I18N_LIBRARY_ALL_' + itemsName.toUpperCase() :
      totalCount === 1 ? selectedItems[0] :
      'I18N_LIBRARY_N_' + itemsName.toUpperCase());
    this.translationData[itemsName + 'Count'] = totalCount;

    // TODO(milit): When the language changes, the translations won't
    // change until the user changes the selection and this function is
    // re-executed.
    if (selectedItems.length > 0) {
      var translatedItems = [];
      for (var i = 0; i < selectedItems.length; i++) {
        translatedItems.push(this.translateService.getInterpolatedString(selectedItems[i]));
      }
      this.selectionDetails[itemsType].description = (
        translatedItems.join(', '));
    } else {
      this.selectionDetails[itemsType].description = (
        'I18N_LIBRARY_ALL_' + itemsName.toUpperCase() + '_SELECTED');
    }
  };

  isSearchInProgress(): boolean {
    return this.searchService.isSearchInProgress();
  };

  deselectAll(itemsType): void{
    this.selectionDetails[itemsType].selections = {};
    this.updateSelectionDetails(itemsType);
    this.onSearchQueryChangeExec();
  };

  toggleSelection(itemsType, optionName): void{
    var selections = this.selectionDetails[itemsType].selections;
    if (!selections.hasOwnProperty(optionName)) {
      selections[optionName] = true;
    } else {
      selections[optionName] = !selections[optionName];
    }

    this.updateSelectionDetails(itemsType);
    this.onSearchQueryChangeExec();
  };

  onSearchQueryChangeExec(): void {
    console.log("hello")
    this.searchService.executeSearchQuery(
      this.searchQuery, this.selectionDetails.categories.selections,
      this.selectionDetails.languageCodes.selections, () => {
        var searchUrlQueryString = this.searchService.getSearchUrlQueryString(
          this.searchQuery, this.selectionDetails.categories.selections,
          this.selectionDetails.languageCodes.selections
        );
        if (this.windowRef.nativeWindow.location.pathname === '/search/find') {
          this.windowRef.nativeWindow.location.search ='/find?q=' + searchUrlQueryString;
        } else {
          this.windowRef.nativeWindow.location.href = '/search/find?q=' + searchUrlQueryString;
        }
      });
  };

  updateSearchFieldsBasedOnUrlQuery(): void {
    this.selectionDetails.categories.selections = {};
    this.selectionDetails.languageCodes.selections = {};

    this.updateSelectionDetails('categories');
    this.updateSelectionDetails('languageCodes');

    var newQuery = (
      this.searchService.updateSearchFieldsBasedOnUrlQuery(
        this.windowRef.nativeWindow.location.search, this.selectionDetails));

    if (this.searchQuery !== newQuery) {
      this.searchQuery = newQuery;
      this.onSearchQueryChangeExec();
    }
  };

  /**
   * Opens the submenu.
   * @param {object} evt
   * @param {String} menuName - name of menu, on which
   * open/close action to be performed (category,language).
   */
  openSubmenu(evt, menuName): void {
    this.navigationService.openSubmenu(evt, menuName);
  };
  /**
   * Handles keydown events on menus.
   * @param {object} evt
   * @param {String} menuName - name of menu to perform action
   * on(category/language)
   * @param {object} eventsTobeHandled - Map keyboard events('Enter') to
   * corresponding actions to be performed(open/close).
   *
   * @example
   *  onMenuKeypress($event, 'category', {enter: 'open'})
   */
  onMenuKeypress(evt, menuName, eventsTobeHandled): void {
    this.navigationService.onMenuKeypress(evt, menuName, eventsTobeHandled);
    this.activeMenuName =  this.navigationService.activeMenuName;
  };

  ngOnDestroy() {
    this.directiveSubscriptions.unsubscribe();
  };
}


angular.module('oppia').directive(
  'searchBar', downgradeComponent({component: SearchBarComponent}));
