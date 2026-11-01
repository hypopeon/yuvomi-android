// Writes upstream's OpenAPI document as JSON, built from upstream *source*.
//
// Usage: node extract_openapi.mjs <upstream-checkout> <out.json> <version>
//
// The running server only serves /api/v1/openapi.json to admins, so the
// snapshot is built the same way the server builds it: by calling
// buildOpenApiSpec() from server/openapi.js. That module and everything it
// imports use Node built-ins only, so no `npm install` is needed.
import { writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const [, , checkout, out, version] = process.argv;
if (!checkout || !out || !version) {
  console.error('usage: node extract_openapi.mjs <upstream-checkout> <out.json> <version>');
  process.exit(2);
}

const moduleUrl = pathToFileURL(resolve(checkout, 'server/openapi.js')).href;
const { buildOpenApiSpec } = await import(moduleUrl);
const spec = buildOpenApiSpec({}, version);
writeFileSync(out, `${JSON.stringify(spec, null, 2)}\n`);
const operations = Object.values(spec.paths)
  .flatMap((item) => Object.keys(item))
  .filter((m) => ['get', 'post', 'put', 'patch', 'delete'].includes(m)).length;
console.log(`openapi: ${Object.keys(spec.paths).length} paths, ${operations} operations -> ${out}`);
