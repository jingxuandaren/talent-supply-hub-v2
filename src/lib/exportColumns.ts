const INDUSTRY_EXCLUDED = [
  '行业大类',
  '推荐优先级',
  '是否补充推荐',
  '星图作者一级分类(T-3标签)',
  '星图作者二级分类(T-3标签)',
];

const NODE_EXCLUDED = [
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

export function normalizeExportHeader(value: unknown): string {
  return String(value ?? '')
    .normalize('NFKC')
    .replace(/\s+/g, '')
    .toLowerCase();
}

export function filterExportColumns(
  fileLabel: string,
  headers: readonly unknown[],
  rows: readonly (readonly unknown[])[],
) {
  const excluded = fileLabel.startsWith('节点')
    ? NODE_EXCLUDED
    : fileLabel.startsWith('行业')
      ? INDUSTRY_EXCLUDED
      : [];
  const blocked = new Set(excluded.map(normalizeExportHeader));
  const indices = headers.flatMap((header, index) =>
    blocked.has(normalizeExportHeader(header)) ? [] : [index],
  );
  return {
    headers: indices.map(index => headers[index]),
    rows: rows.map(row => indices.map(index => row[index])),
  };
}
