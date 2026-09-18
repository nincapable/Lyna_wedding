import { cp, mkdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';

const packageRoot = join(process.cwd(), 'node_modules', 'pdfjs-dist');
const { version } = JSON.parse(await readFile(join(packageRoot, 'package.json'), 'utf8'));
const destination = join(process.cwd(), 'public', 'pdfjs', version);
await mkdir(destination, { recursive: true });
await cp(join(packageRoot, 'LICENSE'), join(destination, 'LICENSE'));
await cp(join(packageRoot, 'legacy', 'build', 'pdf.worker.min.mjs'), join(destination, 'pdf.worker.min.mjs'));
for (const directory of ['standard_fonts', 'cmaps', 'wasm']) {
  await cp(join(packageRoot, directory), join(destination, directory), { recursive: true });
}
