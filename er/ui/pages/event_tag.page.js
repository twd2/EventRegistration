import { NamedPage } from 'er/misc/PageLoader';
import ItemSelectAutoComplete from 'er/components/autocomplete/ItemSelectAutoComplete';

const page = new NamedPage('event_tag', () => {
  ItemSelectAutoComplete.getOrConstruct($('[name="tag"]'), { onItemClick: () => {}, items: getTags });

  function getTags(val) {
    return ['田径', '游泳', '球类', '马约翰杯', '酒井杯', '2017', '2018'];
  }
  function tagSearch() {
    const tag = $('[name="tag"]');
    window.location.href = `/event/tag/${encodeURI(tag.val())}`;
  }

  function tagEnter(e) {
    if (e.keyCode === 13) {
      tagSearch();
    }
  }

  $('[name="search"]').click(() => tagSearch());
  $('[name="tag"]').keydown(e => tagEnter(e));
});

export default page;
