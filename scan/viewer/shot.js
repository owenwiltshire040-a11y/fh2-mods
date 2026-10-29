const {chromium}=require('playwright');
(async()=>{const [,,file,out,views,tgt,lit]=process.argv;
const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const pg=await b.newPage({viewport:{width:1500,height:1000}});
pg.on('console',m=>console.log('console',m.text()));
const u=`http://localhost:8765/index.html?f=${encodeURIComponent(file)}&v=${encodeURIComponent(views)}&t=${encodeURIComponent(tgt||'[0,0.6,0]')}${lit?'&lit=1':''}`;
await pg.goto(u); await pg.waitForFunction(()=>document.title==='done',null,{timeout:240000});
await (await pg.$('canvas')).screenshot({path:out}); await b.close();})();
