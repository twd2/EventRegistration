import _ from 'lodash';

import { NamedPage } from 'er/misc/PageLoader';
import Notification from 'er/components/notification';
import { ConfirmDialog } from 'er/components/dialog';
import UserSelectAutoComplete from 'er/components/autocomplete/UserSelectAutoComplete';

import request from 'er/utils/request';
import tpl from 'er/utils/tpl';
import delay from 'er/utils/delay';
import i18n from 'er/utils/i18n';

const page = new NamedPage('manage_admin', () => {
  UserSelectAutoComplete.getOrConstruct($('[name="username"]'));

  function ensureAndGetSelectedUsers() {
    const users = _.map(
      $('.users tbody [type="checkbox"]:checked'),
      ch => $(ch).closest('tr').attr('data-uid'),
    );
    if (users.length === 0) {
      Notification.error(i18n('请选择至少一个用户来执行此操作。'));
      return null;
    }
    return users;
  }

  async function handleClickRemoveSelected() {
    const selectedUsers = ensureAndGetSelectedUsers();
    if (selectedUsers === null) {
      return;
    }
    const action = await new ConfirmDialog({
      $body: tpl`
        <div class="typo">
          <p>${i18n('确认删除他们的管理员权限吗？')}</p>
        </div>`,
    }).open();
    if (action !== 'yes') {
      return;
    }
    try {
      await request.post('', {
        operation: 'remove',
        uid: selectedUsers,
      });
      Notification.success(i18n('所选用户的管理员权限已删除。'));
      await delay(2000);
      window.location.reload();
    } catch (error) {
      Notification.error(error.message);
    }
  }

  $('[name="remove_selected"]').click(() => handleClickRemoveSelected());
});

export default page;
