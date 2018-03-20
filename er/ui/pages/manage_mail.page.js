import { NamedPage } from 'er/misc/PageLoader';
import UserSelectAutoComplete from 'er/components/autocomplete/UserSelectAutoComplete';

const page = new NamedPage('manage_mail', () => {
  UserSelectAutoComplete.getOrConstruct($('[name="username"]'));
});

export default page;
