import { AutoloadPage } from 'er/misc/PageLoader';
import Dropdown from './Dropdown';

const dropdownPage = new AutoloadPage('dropdownPage', () => {
  Dropdown.registerLifeCycleHooks();
});

export default dropdownPage;
