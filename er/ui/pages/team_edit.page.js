import { NamedPage } from 'er/misc/PageLoader';

const page = new NamedPage('team_edit', () => {
  const item = $('#images');
  const items = $('[name="images_text"]');

  function itemKeyDown(e) {
    if (e.keyCode === 32 || e.keyCode === 188) {
      itemAdd();
      e.preventDefault();
    }
  }

  function itemAdd() {
    items.val(items.val() + ',' + item.val());
    itemsChange();
    item.val('');
  }

  function itemsChange() {
    var itemsText = items.val();
    if (itemsText === '') {
      $('.event__tag').remove();
      return;
    }
    var itemsList = itemsText.split(',').map(item => item.trim())
                           .filter(item => (0 < item.length && item.length <= 500));
    itemsList = Array.from(new Set(itemsList));
    items.val(itemsList.join(','));
    $('.event__tag').remove();
    $.each(itemsList, function(i, item) {
      var str = '<li class="event__tag"><span class="event__tag-link">'
              + '<span class="icon icon-close" style="cursor:pointer"></span>' + item + '</span></li>';
      $('.event__tags').append(str);
    });
    $('.icon-close').click(e => itemRemove(e));
  }

  function itemRemove(e) {
    var it = e.target.closest('.event__tag-link').innerText;
    items.val((',' + items.val() + ',').replace(',' + it + ',', ','));
    itemsChange();
  }

  $('#images').keydown(e => itemKeyDown(e));
  $('#images_add').click(() => itemAdd());

  itemsChange();
});

export default page;
