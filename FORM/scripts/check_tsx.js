
const ts=require('/opt/nvm/versions/node/v22.16.0/lib/node_modules/typescript');
const fs=require('fs');
for (const f of process.argv.slice(2)){
 const src=fs.readFileSync(f,'utf8');
 const out=ts.transpileModule(src,{compilerOptions:{jsx:ts.JsxEmit.Preserve,target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext},reportDiagnostics:true,fileName:f});
 const ds=(out.diagnostics||[]).filter(d=>d.category===ts.DiagnosticCategory.Error);
 console.log(f, ds.length?"ERRORS "+ds.map(d=>ts.flattenDiagnosticMessageText(d.messageText,' ')).join(' | '):"OK");
 process.exitCode ||= ds.length?1:0;
}
