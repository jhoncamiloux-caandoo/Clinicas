const http = require('http');
const fs = require('fs');
const path = require('path');
const ROOT = '/Volumes/Camilo-HD/Lp/Clinicas';
const types = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.ico':'image/x-icon','.webp':'image/webp','.mp4':'video/mp4','.webm':'video/webm','.mov':'video/quicktime'};
http.createServer((req,res)=>{
  let p = decodeURIComponent(req.url.split('?')[0]);
  if(p.endsWith('/')) p+='index.html';
  const fp = path.join(ROOT,p);
  fs.readFile(fp,(err,data)=>{
    if(err){res.writeHead(404);res.end('not found');return;}
    res.writeHead(200,{'Content-Type':types[path.extname(fp)]||'application/octet-stream'});
    res.end(data);
  });
}).listen(4599,()=>console.log('serving on 4599'));
