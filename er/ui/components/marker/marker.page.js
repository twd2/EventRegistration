import { AutoloadPage } from 'er/misc/PageLoader';
import MarkerReactive from './MarkerReactive';

const markerPage = new AutoloadPage('markerPage', () => {
  MarkerReactive.initAll();
});

export default markerPage;
