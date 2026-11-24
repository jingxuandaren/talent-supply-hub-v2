const FIELD_ALIASES: Record<string, string[]> = {
  达人类型: ['一级标签'],
  达人抖音粉丝量级: ['粉丝量级'],
  推荐行业: ['推荐方向', '行业'],
};

/** Keep original columns authoritative; resolve education-specific names only when absent. */
export function getTalentField(
  headers: string[],
  row: unknown[],
  name: string,
) {
  for (const field of [name, ...(FIELD_ALIASES[name] ?? [])]) {
    const index = headers.indexOf(field);
    if (index >= 0) return row[index];
  }
  return undefined;
}
