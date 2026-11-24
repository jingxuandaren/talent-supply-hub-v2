import ownerRewritePolicy from '@/data/nodeSalesOwnerRewrites.json';

export function rewriteNodeSalesOwners<T>(
  headers: readonly unknown[],
  rows: readonly (readonly T[])[],
): T[][] {
  const ownerIndex = headers.findIndex(
    header => String(header ?? '').trim() === ownerRewritePolicy.column,
  );
  if (ownerIndex < 0) return rows.map(row => [...row]);

  const protectedOwners = new Set(ownerRewritePolicy.names);
  return rows.map(row =>
    row.map((value, columnIndex) =>
      columnIndex === ownerIndex &&
      protectedOwners.has(String(value ?? '').trim())
        ? (ownerRewritePolicy.replaceWith as T)
        : value,
    ),
  );
}
