import { NamedPage } from 'er/misc/PageLoader';

const page = new NamedPage('main', () => {
  const $frame = $('#frame');
  setInterval(() => {
    $frame.height($frame.width() / 1400 * 933);
    $(window).resize(() => {
      $frame.height($frame.width() / 1400 * 933);
    });
  }, 100);
});

export default page;
