import sharp from 'sharp';
import jsfeat from 'jsfeat';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';

const SIZE = 512;
let referencePromise;

// Only the violet strokes participate in recognition; card artwork is discarded.
export function purpleMask(pixels, width, height, channels = 3) {
  const mask = new Uint8Array(width * height);
  for (let i = 0; i < mask.length; i++) {
    const r = pixels[i * channels], g = pixels[i * channels + 1], b = pixels[i * channels + 2];
    const max = Math.max(r, g, b), min = Math.min(r, g, b), delta = max - min;
    if (max < 40 || delta / max < .4 || b !== max || delta === 0) continue;
    const hue = 60 * ((r - g) / delta + 4);
    if (hue >= 258 && hue <= 303 && b > g * 1.45 && r > g * 1.1) mask[i] = 255;
  }
  // Discard tiny colour specks, preserving connected segments of the drawing.
  const seen = new Uint8Array(mask.length);
  for (let i = 0; i < mask.length; i++) {
    if (!mask[i] || seen[i]) continue;
    const component = [i]; seen[i] = 1;
    for (let k = 0; k < component.length; k++) {
      const p = component[k], x = p % width, y = Math.floor(p / width);
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        const nx = x + dx, ny = y + dy, n = ny * width + nx;
        if (nx >= 0 && nx < width && ny >= 0 && ny < height && mask[n] && !seen[n]) {
          seen[n] = 1; component.push(n);
        }
      }
    }
    if (component.length < 5) for (const p of component) mask[p] = 0;
  }
  return mask;
}

async function prepare(input) {
  const { data, info } = await sharp(input, { limitInputPixels: 24_000_000 })
    .rotate().resize(1000, 1000, { fit: 'inside', withoutEnlargement: true })
    .flatten({ background: '#fff' }).removeAlpha().toColourspace('srgb').raw().toBuffer({ resolveWithObject: true });
  const mask = purpleMask(data, info.width, info.height, info.channels);
  let minX = info.width, minY = info.height, maxX = 0, maxY = 0, count = 0;
  for (let i = 0; i < mask.length; i++) if (mask[i]) {
    const x = i % info.width, y = Math.floor(i / info.width);
    minX = Math.min(minX, x); maxX = Math.max(maxX, x);
    minY = Math.min(minY, y); maxY = Math.max(maxY, y); count++;
  }
  if (count < 250 || maxX - minX < 60 || maxY - minY < 60) return null;
  const normalized = await sharp(Buffer.from(mask), { raw: { width: info.width, height: info.height, channels: 1 } })
    .extract({ left: minX, top: minY, width: maxX - minX + 1, height: maxY - minY + 1 })
    .resize(SIZE - 48, SIZE - 48, { fit: 'contain', background: '#000' })
    .extend({ top: 24, bottom: 24, left: 24, right: 24, background: '#000' })
    .greyscale().raw().toBuffer();
  const points = [];
  const binary = new Uint8Array(SIZE * SIZE);
  for (let i = 0; i < normalized.length; i++) if (normalized[i] > 55) {
    binary[i] = 1;
    points.push({ x: i % SIZE, y: Math.floor(i / SIZE) });
  }
  return { normalized, binary, points, features: features(normalized) };
}

function orientation(image, x, y) {
  let mx = 0, my = 0;
  for (let dy = -15; dy <= 15; dy++) {
    const radius = Math.floor(Math.sqrt(225 - dy * dy));
    for (let dx = -radius; dx <= radius; dx++) {
      const value = image.data[(y + dy) * image.cols + x + dx];
      mx += dx * value; my += dy * value;
    }
  }
  return Math.atan2(my, mx);
}

function features(normalized) {
  const all = [];
  for (const size of [512, 384, 256]) {
    const image = new jsfeat.matrix_t(size, size, jsfeat.U8C1_t);
    const source = new jsfeat.matrix_t(SIZE, SIZE, jsfeat.U8C1_t);
    source.data.set(normalized);
    if (size === SIZE) image.data.set(normalized);
    else jsfeat.imgproc.resample(source, image, size, size);
    const corners = Array.from({ length: size * size }, () => new jsfeat.keypoint_t());
    jsfeat.yape06.laplacian_threshold = 20;
    jsfeat.yape06.min_eigen_value_threshold = 15;
    const count = jsfeat.yape06.detect(image, corners, 20);
    const selected = corners.slice(0, count).sort((a, b) => b.score - a.score).slice(0, 500);
    for (const corner of selected) corner.angle = orientation(image, corner.x, corner.y);
    const blurred = new jsfeat.matrix_t(size, size, jsfeat.U8C1_t);
    jsfeat.imgproc.gaussian_blur(image, blurred, 5, 1);
    const descriptors = new jsfeat.matrix_t(32, selected.length, jsfeat.U8C1_t);
    jsfeat.orb.describe(blurred, selected, selected.length, descriptors);
    for (let i = 0; i < selected.length; i++) all.push({
      x: selected[i].x * SIZE / size, y: selected[i].y * SIZE / size,
      descriptor: new Uint32Array(descriptors.buffer.u8.buffer.slice(i * 32, i * 32 + 32)),
    });
  }
  return all;
}

function popcount(value) {
  value -= (value >>> 1) & 0x55555555;
  value = (value & 0x33333333) + ((value >>> 2) & 0x33333333);
  return (((value + (value >>> 4)) & 0x0f0f0f0f) * 0x01010101) >>> 24;
}

function matches(reference, photograph) {
  const result = [], used = new Set();
  for (const point of reference) {
    let best = 257, second = 257, candidate = -1;
    for (let i = 0; i < photograph.length; i++) {
      let distance = 0;
      for (let k = 0; k < 8; k++) distance += popcount(point.descriptor[k] ^ photograph[i].descriptor[k]);
      if (distance < best) { second = best; best = distance; candidate = i; }
      else if (distance < second) second = distance;
    }
    if (best < 65 && best < second * .8 && !used.has(candidate)) {
      used.add(candidate); result.push({ from: point, to: photograph[candidate] });
    }
  }
  return result;
}

function project(matrix, point) {
  const w = matrix[6] * point.x + matrix[7] * point.y + matrix[8];
  return { x: (matrix[0] * point.x + matrix[1] * point.y + matrix[2]) / w,
    y: (matrix[3] * point.x + matrix[4] * point.y + matrix[5]) / w };
}

function near(mask, point) {
  if (!Number.isFinite(point.x) || !Number.isFinite(point.y)) return false;
  const x = Math.round(point.x), y = Math.round(point.y);
  for (let dy = -4; dy <= 4; dy++) for (let dx = -4; dx <= 4; dx++) {
    if (dx * dx + dy * dy > 16) continue;
    const nx = x + dx, ny = y + dy;
    if (nx >= 0 && ny >= 0 && nx < SIZE && ny < SIZE && mask[ny * SIZE + nx]) return true;
  }
  return false;
}

function coverage(reference, photograph, model) {
  const inverse = new jsfeat.matrix_t(3, 3, jsfeat.F32C1_t);
  jsfeat.matmath.invert_3x3(model, inverse);
  const totals = Array(9).fill(0), hits = Array(9).fill(0);
  let covered = 0, precision = 0;
  for (const point of reference.points) {
    const region = Math.min(2, Math.floor(point.y * 3 / SIZE)) * 3 + Math.min(2, Math.floor(point.x * 3 / SIZE));
    totals[region]++;
    if (near(photograph.binary, project(model.data, point))) { covered++; hits[region]++; }
  }
  for (const point of photograph.points) if (near(reference.binary, project(inverse.data, point))) precision++;
  const regions = totals.map((n, i) => n > 50 ? hits[i] / n : null);
  return { coverage: covered / reference.points.length, precision: precision / photograph.points.length, regions };
}

/** Compare the assembled dragon, allowing perspective, rotation and missing overlap strokes. */
export async function recognizeDragon(input) {
  if (!referencePromise) referencePromise = readFile(join(process.cwd(), 'scan-reference', 'dragon.png')).then(prepare);
  const reference = await referencePromise;
  if (!reference) throw new Error('INVALID_REFERENCE');
  const photograph = await prepare(input);
  if (!photograph) return { accepted: false, reason: 'violet', coverage: 0, precision: 0 };
  const pairs = matches(reference.features, photograph.features);
  if (pairs.length < 14) return { accepted: false, reason: 'alignment', coverage: 0, precision: 0 };
  const from = pairs.map(pair => pair.from), to = pairs.map(pair => pair.to);
  const kernel = new jsfeat.motion_model.homography2d();
  const model = new jsfeat.matrix_t(3, 3, jsfeat.F32C1_t);
  const inliers = new jsfeat.matrix_t(pairs.length, 1, jsfeat.U8C1_t);
  const params = new jsfeat.ransac_params_t(4, 4, .65, .995);
  if (!jsfeat.motion_estimator.ransac(params, kernel, from, to, pairs.length, model, inliers, 1800)) {
    return { accepted: false, reason: 'alignment', coverage: 0, precision: 0 };
  }
  const good = pairs.filter((_, i) => inliers.data[i]);
  if (good.length < 12) return { accepted: false, reason: 'alignment', coverage: 0, precision: 0 };
  kernel.run(good.map(pair => pair.from), good.map(pair => pair.to), model, good.length);
  // A physical assembly cannot mirror the drawing or collapse it into one small region.
  const corners = [{ x: 24, y: 24 }, { x: 488, y: 24 }, { x: 488, y: 488 }, { x: 24, y: 488 }].map(p => project(model.data, p));
  let area = 0;
  for (let i = 0; i < 4; i++) {
    const p = corners[i], q = corners[(i + 1) % 4]; area += p.x * q.y - q.x * p.y;
  }
  if (!Number.isFinite(area) || area < SIZE * SIZE * .5 || area > SIZE * SIZE * 3) {
    return { accepted: false, reason: 'alignment', coverage: 0, precision: 0 };
  }
  const score = coverage(reference, photograph, model);
  const occupied = score.regions.filter(value => value !== null);
  const enoughRegions = occupied.filter(value => value >= .45).length >= Math.ceil(occupied.length * .8);
  const accepted = score.coverage >= .7 && score.precision >= .67 && enoughRegions && occupied.every(value => value >= .25);
  return { accepted, reason: accepted ? 'match' : 'incomplete', coverage: score.coverage, precision: score.precision };
}
