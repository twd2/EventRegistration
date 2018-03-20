import 'jquery.transit';

import 'normalize.css/normalize.css';
import 'codemirror/lib/codemirror.css';

import _ from 'lodash';

import 'er/misc/float.styl';
import 'er/misc/typography.styl';
import 'er/misc/textalign.styl';
import 'er/misc/grid.styl';
import 'er/misc/slideout.styl';

import 'er/misc/.iconfont/webicon.styl';
import 'er/misc/immersive.styl';
import 'er/misc/structure.styl';
import 'er/misc/section.styl';
import 'er/misc/nothing.styl';

import { PageLoader } from 'er/misc/PageLoader';
import delay from 'er/utils/delay';

// eslint-disable-next-line camelcase
__webpack_public_path__ = '/'; // TODO(twd2)

const pageLoader = new PageLoader();

const currentPage = pageLoader.getNamedPage(document.documentElement.getAttribute('data-page'));
const includedPages = pageLoader.getAutoloadPages();

function buildSequence(pages, type) {
  if (process.env.NODE_ENV !== 'production') {
    if (['before', 'after'].indexOf(type) === -1) {
      // eslint-disable-next-line quotes
      throw new Error(`'type' should be one of 'before' or 'after'`);
    }
  }
  return pages
    .filter(p => p && p[`${type}Loading`])
    .map(p => ({
      page: p,
      func: p[`${type}Loading`],
      type,
    }));
}

async function load() {
  const loadSequence = [
    ...buildSequence(includedPages, 'before'),
    ...buildSequence([currentPage], 'before'),
    ...buildSequence(includedPages, 'after'),
    ...buildSequence([currentPage], 'after'),
  ];
  // eslint-disable-next-line no-restricted-syntax
  for (const { page, func, type } of loadSequence) {
    if (typeof func !== 'function') {
      if (process.env.NODE_ENV !== 'production') {
        throw new Error(`The '${type}Loading' function of '${page.name}' is not callable`);
      }
      continue;
    }
    if (process.env.NODE_ENV !== 'production') {
      console.time(`${page.name}: ${type}Loading`);
    }
    try {
      await func();
    } catch (e) {
      console.error(`Failed to call '${type}Loading' of ${page.name}\n${e.stack}`);
    }
    if (process.env.NODE_ENV !== 'production') {
      console.timeEnd(`${page.name}: ${type}Loading`);
    }
  }
  const sections = _.map($('.section').get(), (section, idx) => ({
    shouldDelay: idx < 5, // only animate first 5 sections
    $element: $(section),
  }));
  // eslint-disable-next-line no-restricted-syntax
  for (const { $element, shouldDelay } of sections) {
    $element.addClass('visible');
    if (shouldDelay) {
      await delay(50);
    }
  }
  await delay(500);
  // eslint-disable-next-line no-restricted-syntax
  for (const { $element } of sections) {
    $element.trigger('erLayout');
  }
  $(document).trigger('erPageFullyInitialized');
}

load();
