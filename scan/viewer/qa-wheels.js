// Render opposite-side and rear views from immutable snapshots of built car geometry.
const {chromium}=require('playwright');
const fs=require('fs');
(async()=>{
 const jobs=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
 const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:816,height:459}});
 for(const job of jobs){
  for(const [name,yaw] of [['other-side',50],['rear',150]]){
   await page.goto(`http://127.0.0.1:8767/thumb.html?f=${encodeURIComponent(job.file)}&w=816&h=459&yaw=${yaw}&pitch=10`);
   await page.waitForFunction(()=>document.title==='done',null,{timeout:120000});
   await (await page.$('canvas')).screenshot({path:job.out+'/'+name+'.png',omitBackground:true});
  }
  process.stdout.write(job.slug+' rendered both additional views\n');
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
