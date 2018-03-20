import { NamedPage } from 'er/misc/PageLoader';
import UserSelectAutoComplete from 'er/components/autocomplete/UserSelectAutoComplete';

const page = new NamedPage('register_force', () => {
  UserSelectAutoComplete.getOrConstruct($('[name="username"]'));
});

export default page;
