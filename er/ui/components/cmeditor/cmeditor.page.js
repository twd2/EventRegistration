import { AutoloadPage } from 'er/misc/PageLoader';
import delay from 'er/utils/delay';
import CmEditor from '.';

import 'vj-simplemde/src/css/simplemde.css';
import './cmeditor.styl';

function runSubstitute($container) {
  const selector = ['textarea[data-markdown]'];
  $container.find(selector.join(', ')).get().forEach((element) => {
    CmEditor.getOrConstruct($(element));
  });
}

const cmEditorPage = new AutoloadPage('cmEditorPage', () => {
  runSubstitute($('body'));
  $(document).on('vjContentNew', async (e) => {
    await delay(0);
    runSubstitute($(e.target));
  });
});

export default cmEditorPage;
