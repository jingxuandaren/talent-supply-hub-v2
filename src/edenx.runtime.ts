import { defineRuntimeConfig } from '@edenx/runtime';

const basename =
  typeof window !== 'undefined' &&
  window.location.hostname.endsWith('.github.io')
    ? `/${window.location.pathname.split('/').filter(Boolean)[0] || ''}`
    : '/';

export default defineRuntimeConfig({ router: { basename } });
