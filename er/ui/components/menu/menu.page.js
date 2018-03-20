import { AutoloadPage } from 'er/misc/PageLoader';
import { slideDown } from 'er/utils/slide';
import delay from 'er/utils/delay';

function expandMenu($menu) {
  slideDown($menu, 500, { opacity: 0 }, { opacity: 1 });
}

async function expandAllMenus() {
  await delay(200);
  $('.menu.collapsed').get().forEach(menu => expandMenu($(menu)));
}

const menuPage = new AutoloadPage('menuPage', () => {
  expandAllMenus();
});

export default menuPage;
