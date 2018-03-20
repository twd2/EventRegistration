import _ from 'lodash';
import tpl from 'er/utils/tpl';
import DOMAttachedObject from 'er/components/DOMAttachedObject';
import AutoComplete from '.';

function getText(item) {
  return item;
}

function renderItem(item) {
  return tpl`
    <div class="media">
      <div class="media__body medium">
        <div class="tag-select">${item}</div>
      </div>
    </div>
  `;
}

export default class ItemSelectAutoComplete extends AutoComplete {
  static DOMAttachKey = 'vjItemSelectAutoCompleteInstance';

  constructor($dom, options) {
    super($dom, {
      classes: 'item-select',
      render: renderItem,
      text: getText,
      minChar: 0,
      ...options,
    });
  }

  onItemClick(ev) {
    super.onItemClick(ev);
    this.options.onItemClick();
  }
}

_.assign(ItemSelectAutoComplete, DOMAttachedObject);
