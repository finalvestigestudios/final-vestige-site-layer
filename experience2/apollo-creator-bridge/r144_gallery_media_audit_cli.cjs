'use strict';
/** Offline: node r144_gallery_media_audit_cli.cjs /path/to/read-only-wp-export.html */
const fs=require('node:fs');
const {inspect}=require('./r144_gallery_media_custody.cjs');
const input=process.argv[2];
if(!input){console.error('Usage: node r144_gallery_media_audit_cli.cjs READ_ONLY_HTML_EXPORT');process.exitCode=64;}
else {
 try {
  const result=inspect(fs.readFileSync(input,'utf8'));
  process.stdout.write(JSON.stringify(result,null,2)+'\n');
  if(result.blockers.length)process.exitCode=2;
 } catch(err){console.error('STAGING_HOLD:',err.message);process.exitCode=2;}
}
