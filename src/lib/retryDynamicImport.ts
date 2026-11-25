type DynamicImportFactory<T> = () => Promise<T>;

export function retryDynamicImport<T>(
  load: DynamicImportFactory<T>,
  attempts = 3,
  baseDelay = 350,
): Promise<T> {
  return new Promise((resolve, reject) => {
    let attempt = 0;

    const run = () => {
      attempt += 1;
      load()
        .then(resolve)
        .catch((error: unknown) => {
          if (attempt >= attempts) {
            reject(error);
            return;
          }
          globalThis.setTimeout(run, baseDelay * attempt);
        });
    };

    run();
  });
}
