import { AutoloadPage } from 'er/misc/PageLoader';
import Tab from './Tab';

const tabPage = new AutoloadPage('tabPage', () => {
  Tab.initAll();
  Tab.initEventListeners();
});

export default tabPage;
