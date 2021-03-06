import { NamedPage } from 'er/misc/PageLoader';
import { ConfirmDialog } from 'er/components/dialog';
import UserSelectAutoComplete from 'er/components/autocomplete/UserSelectAutoComplete';

import tpl from 'er/utils/tpl';
import i18n from 'er/utils/i18n';

const page = new NamedPage('event_detail', () => {
  const teammate = $('#teammate');
  const teammates = $('[name="teammates"]');

  if ($('#teammate').length && $('#team_leader').length) {
    UserSelectAutoComplete.getOrConstruct($('#teammate'));
    UserSelectAutoComplete.getOrConstruct($('#team_leader'), { clearDefaultValue: false });

    var item, items;

    function verifyItem() {
      item = teammate;
      items = teammates;
    }

    function itemKeyDown(e) {
      if (e.keyCode === 32 || e.keyCode === 188) {
        itemAdd();
        e.preventDefault();
      }
    }

    function itemAdd() {
      verifyItem();
      items.val(items.val() + ',' + item.val());
      itemsChange();
      item.val('');
    }

    function itemsChange() {
      verifyItem();
      var itemsText = items.val();
      if (itemsText === '') {
        $('.register__teammate').remove();
        return;
      }
      var itemsList = itemsText.split(',').map(item => item.trim())
                             .filter(item => (0 < item.length && item.length <= 64));
      itemsList = Array.from(new Set(itemsList));
      items.val(itemsList.join(','));
      $('.register__teammate').remove();
      $.each(itemsList, function(i, item) {
        var str = '<li class="register__teammate"><span class="register__teammate-link">'
                + '<span class="icon icon-close" style="cursor:pointer"></span>' + item + '</span></li>';
        $('.register__teammates').append(str);
      });
      $('.icon-close').click(e => itemRemove(e));
    }

    function itemRemove(e) {
      verifyItem();
      var it = e.target.closest('.register__teammate-link').innerText;
      items.val((',' + items.val() + ',').replace(',' + it + ',', ','));
      itemsChange();
    }

    $('#teammate').keydown(e => itemKeyDown(e));
    $('#teammate_add').click(() => itemAdd());

    itemsChange('teammate');
  }

  async function handleClickRemoveConfirm(ev) {
    ev.preventDefault();
    const action = await new ConfirmDialog({
      $body: tpl`
        <div class="typo">
          <p>${i18n('确认删除赛事吗？')}</p>
        </div>`,
    }).open();
    if (action == 'yes') {
      ev.target.closest('form').submit();
    }
  }
  $('#remove_event').click(ev => handleClickRemoveConfirm(ev));

  async function handleClickRemoveConfirm(ev) {
    ev.preventDefault();
    const action = await new ConfirmDialog({
      $body: tpl`
        <div class="typo">
          <p>${i18n('确认取消报名吗？')}</p>
        </div>`,
    }).open();
    if (action == 'yes') {
      ev.target.closest('form').submit();
    }
  }

  $('#remove_selected').click(ev => handleClickRemoveConfirm(ev));
});

export default page;
