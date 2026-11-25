import { retryDynamicImport } from '@/lib/retryDynamicImport';
import { Component, Suspense, lazy, useEffect, useState } from 'react';
import type { ReactNode } from 'react';

const AgencyModule = lazy(() =>
  retryDynamicImport(() =>
    import('./AgencyModule').then(module => ({
      default: module.AgencyModule,
    })),
  ),
);

const P0AuthorsModule = lazy(() =>
  retryDynamicImport(() =>
    import('./P0AuthorsModule').then(module => ({
      default: module.P0AuthorsModule,
    })),
  ),
);

export function preloadAgencyModules() {
  if (typeof window === 'undefined') return;
  const schedule =
    window.requestIdleCallback ??
    ((callback: IdleRequestCallback) =>
      window.setTimeout(
        () => callback({ didTimeout: false, timeRemaining: () => 0 }),
        1200,
      ));
  schedule(() => {
    Promise.all([
      retryDynamicImport(() => import('./AgencyModule')),
      retryDynamicImport(() => import('./P0AuthorsModule')),
    ]).catch(() => {
      // 用户真正进入代理商模块时会再次尝试并展示可恢复的错误面板。
    });
  });
}

class AgencyErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean }
> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <div className="state-panel error-panel" role="alert">
        <div>
          <strong>代理商模块暂时加载失败</strong>
          <p>网络抖动或静态资源更新可能导致加载中断，请刷新页面后重试。</p>
        </div>
        <button type="button" onClick={() => window.location.reload()}>
          重新加载
        </button>
      </div>
    );
  }
}

function AgencyLoadingFallback() {
  const [showRecovery, setShowRecovery] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => setShowRecovery(true), 8000);
    return () => window.clearTimeout(timer);
  }, []);

  if (showRecovery) {
    return (
      <output className="state-panel">
        <div>
          <strong>代理商模块加载时间较长</strong>
          <p>请检查当前网络，或刷新页面重新获取模块资源。</p>
        </div>
        <button type="button" onClick={() => window.location.reload()}>
          刷新页面
        </button>
      </output>
    );
  }

  return <div className="state-panel">正在加载代理商模块，请稍候…</div>;
}

function AgencyModules() {
  return (
    <>
      <AgencyModule />
      <P0AuthorsModule />
    </>
  );
}

export function LazyAgencyModules() {
  return (
    <AgencyErrorBoundary>
      <Suspense fallback={<AgencyLoadingFallback />}>
        <AgencyModules />
      </Suspense>
    </AgencyErrorBoundary>
  );
}
