import { NamedPage } from 'er/misc/PageLoader';
import { ConfirmDialog } from 'er/components/dialog';

import tpl from 'er/utils/tpl';
import i18n from 'er/utils/i18n';

const page = new NamedPage('register_detail', () => {
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
