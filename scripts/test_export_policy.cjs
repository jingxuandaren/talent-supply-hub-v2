const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
const root = path.resolve(__dirname, '..');
const columns = { exports: {} };
const compile = file =>
  ts.transpileModule(fs.readFileSync(file, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS },
  }).outputText;
vm.runInNewContext(compile(path.join(root, 'src/lib/exportColumns.ts')), {
  exports: columns.exports,
  module: columns,
  Set,
});
const normalize = columns.exports.normalizeExportHeader;
const forbidden = [
  '行业大类',
  '节点行业内排名',
  '推荐优先级',
  '是否重点推荐(行业千人池)',
  '星图作者一级分类(T-3标签)',
  '星图作者二级分类(T-3标签)',
  '节点推荐分',
  '入池逻辑',
  '是否补充入池',
  '行业自然命中',
  '商业行业命中',
  '内容标签命中',
  '画像Bench命中',
  '行业画像Bench',
  '最高视频报价(元)',
  '节点规则摘要',
];
const blocked = new Set(forbidden.map(normalize));
const fixture = columns.exports.filterExportColumns(
  '节点-测试.csv',
  [
    '行业 大类',
    '节点行业内排名',
    '是否重点推荐（行业千人池）',
    '星图作者一级分类（T-3 标签）',
    '有效字段',
  ],
  [[1, 2, 3, 4, '保留']],
);
assert.deepEqual(JSON.parse(JSON.stringify(fixture)), {
  headers: ['有效字段'],
  rows: [['保留']],
});
let blob;
const table = { exports: {} };
vm.runInNewContext(compile(path.join(root, 'src/lib/tableCsv.ts')), {
  exports: table.exports,
  module: table,
  require: () => columns.exports,
  Blob,
  URL: {
    createObjectURL: value => {
      blob = value;
      return 'blob:test';
    },
    revokeObjectURL() {},
  },
  document: {
    createElement: () => ({ style: {}, click() {}, remove() {} }),
    body: { appendChild() {} },
  },
  window: { setTimeout() {} },
});
function parseCsv(csv) {
  const rows = [];
  let row = [];
  let field = '';
  let quoted = false;
  for (let i = 0; i < csv.length; i++) {
    const c = csv[i];
    if (c === '"') {
      if (quoted && csv[i + 1] === '"') {
        field += '"';
        i++;
      } else quoted = !quoted;
    } else if (c === ',' && !quoted) {
      row.push(field);
      field = '';
    } else if (c === '\n' && !quoted) {
      row.push(field.replace(/\r$/, ''));
      rows.push(row);
      row = [];
      field = '';
    } else field += c;
  }
  row.push(field);
  rows.push(row);
  return rows;
}
(async () => {
  const results = [];
  for (const filename of fs
    .readdirSync(path.join(root, 'download-assets'))
    .filter(f => f.endsWith('.data'))) {
    const data = JSON.parse(
      fs.readFileSync(path.join(root, 'download-assets', filename), 'utf8'),
    );
    const node = filename.startsWith('node-');
    if (!node && !filename.startsWith('industry-')) continue;
    table.exports.downloadRowsTable(
      `${node ? '节点' : '行业'}-测试.csv`,
      data.headers,
      data.rows,
    );
    const csv = await blob.text();
    const parsed = parseCsv(csv.replace(/^\uFEFF/, ''));
    assert.equal(parsed.length - 1, data.rows.length);
    const normalized = parsed[0].map(normalize);
    assert(!normalized.includes(normalize('行业大类')));
    if (node) {
      assert.equal(data.rows.length, 16500);
      assert(normalized.every(h => !blocked.has(h)));
    }
    const idIndex = parsed[0].indexOf('达人星图id');
    assert(idIndex >= 0);
    if (data.rows[0][data.headers.indexOf('达人星图id')])
      assert(parsed[1][idIndex].startsWith('="'));
    results.push({
      file: filename,
      rows: parsed.length - 1,
      columns: parsed[0].length,
    });
  }
  console.log(JSON.stringify(results, null, 2));
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
