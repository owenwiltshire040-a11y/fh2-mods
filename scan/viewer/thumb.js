// node thumb.js car.glb out.png [w] [h] [yaw] [pitch]  — needs `python3 -m http.server 8765` running in scan/viewer
const {chromium} = require('playwright');
(async () => {
  const [, , file, out, w = 816, h = 459, yaw = -35, pitch = 9] = process.argv;
  const b = await chromium.launch({args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader']});
  const pg = await b.newPage({viewport: {width: +w, height: +h}});
  pg.on('console', m => console.log('console', m.text()));
  await pg.goto(`http://localhost:8765/thumb.html?f=${encodeURIComponent(file)}&w=${w}&h=${h}&yaw=${yaw}&pitch=${pitch}`);
  await pg.waitForFunction(() => document.title === 'done', null, {timeout: 240000});
  await (await pg.$('canvas')).screenshot({path: out, omitBackground: true});
  await b.close();
})();
