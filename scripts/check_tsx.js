const fs = require('fs');
const path = require('path');
const ts = require('typescript');

const files = process.argv.slice(2);
let hasError = false;

for (const file of files) {
  const filePath = path.resolve(process.cwd(), file);
  if (!fs.existsSync(filePath)) {
    console.error(`File not found: ${file}`);
    hasError = true;
    continue;
  }
  const content = fs.readFileSync(filePath, 'utf8');
  const result = ts.transpileModule(content, {
    compilerOptions: {
      jsx: ts.JsxEmit.ReactJSX,
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.ESNext,
    },
    fileName: filePath,
    reportDiagnostics: true,
  });

  if (result.diagnostics && result.diagnostics.length > 0) {
    console.error(`Errors in ${file}:`, result.diagnostics);
    hasError = true;
  } else {
    console.log(`✓ ${file} syntax OK`);
  }
}

process.exit(hasError ? 1 : 0);
