import { NamedPage } from 'er/misc/PageLoader';

const page = new NamedPage('user_message', () => {
  $('[name="filter-form"] [name="unread_only"]').change(() => {
    $('[name="filter-form"]').submit();
  });
});

export default page;
