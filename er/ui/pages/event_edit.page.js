import { NamedPage } from 'er/misc/PageLoader';
import ItemSelectAutoComplete from 'er/components/autocomplete/ItemSelectAutoComplete';

const page = new NamedPage('event_edit', () => {
  ItemSelectAutoComplete.getOrConstruct($('#tag'), { onItemClick: () => itemAdd('tag'), items: () => getTags('') });
  ItemSelectAutoComplete.getOrConstruct($('#field'), { onItemClick: () => itemAdd('field'), items: () => getFields('') });

  const tag = $('#tag');
  const tags = $('[name="tags"]');
  const field = $('#field');
  const fields = $('[name="fields"]');
  var item, items;

  function getTags(val) {
    return ['田径', '游泳', '球类', '马约翰杯', '酒井杯', '2018', '2019', '2020', '2021'];
  }

  function getFields(val) {
    return ['队名', '身高', '体重'];
  }

  function verifyItem(mode) {
    if (mode === 'tag') {
      item = tag;
      items = tags;
    } else {
      item = field;
      items = fields;
    }
  }

  function itemKeyDown(e, mode) {
    if (e.keyCode === 32 || e.keyCode === 188) {
      itemAdd(mode);
      e.preventDefault();
    }
  }

  function itemAdd(mode) {
    verifyItem(mode);
    items.val(items.val() + ',' + item.val());
    itemsChange(mode);
    item.val('');
  }

  function itemsChange(mode) {
    verifyItem(mode);
    var itemsText = items.val();
    if (itemsText === '') {
      $('.event__' + mode).remove();
      return;
    }
    var itemsList = itemsText.split(',').map(item => item.trim())
                           .filter(item => (0 < item.length && item.length <= 64));
    itemsList = Array.from(new Set(itemsList));
    items.val(itemsList.join(','));
    $('.event__' + mode).remove();
    $.each(itemsList, function(i, item) {
      var str = '<li class="event__' + mode + '"><span class="event__' + mode + '-link">'
              + '<span class="icon icon-close" style="cursor:pointer"></span>' + item + '</span></li>';
      $('.event__' + mode + 's').append(str);
    });
    $('.icon-close').click(e => itemRemove(e, mode));
  }

  function itemRemove(e, mode) {
    verifyItem(mode);
    var it = e.target.closest('.event__' + mode + '-link').innerText;
    items.val((',' + items.val() + ',').replace(',' + it + ',', ','));
    itemsChange(mode);
  }

  function groupCheck() {
    if ($('[name="is_group"]').is(':checked')) {
      $('#member_limit').show();
      $('[name="member_lb"]').prop('disabled', false);
      $('[name="member_ub"]').prop('disabled', false);
    } else {
      $('#member_limit').hide();
      $('[name="member_lb"]').prop('disabled', true);
      $('[name="member_ub"]').prop('disabled', true);
    }
  }

  $('#tag').keydown(e => itemKeyDown(e, 'tag'));
  $('#tag_add').click(() => itemAdd('tag'));
  $('#field').keydown(e => itemKeyDown(e, 'field'));
  $('#field_add').click(() => itemAdd('field'));
  $('[name="is_group"]').change(() => groupCheck());

  itemsChange('tag');
  itemsChange('field');
  groupCheck();
});

export default page;
