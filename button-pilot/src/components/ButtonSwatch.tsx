import type { HoleType, Material } from "@/lib/schema";

/**
 * Pure SVG render of a garment button. No photos required — consistent,
 * infinitely scalable, tinted by the variant's colorHex, and varied by hole
 * type. Doubles as a catalog image and a color/finish swatch.
 *
 * It's a plain server-renderable component (no interactivity), so it works
 * inside Server Components and ships zero client JS.
 */

type Props = {
  colorHex: string;
  holeType: HoleType;
  material: Material;
  size?: number; // px
  label?: string;
  className?: string;
};

function shade(hex: string, amount: number): string {
  // amount in [-1,1]; positive lightens, negative darkens.
  const n = hex.replace("#", "");
  const r = parseInt(n.slice(0, 2), 16);
  const g = parseInt(n.slice(2, 4), 16);
  const b = parseInt(n.slice(4, 6), 16);
  const adj = (c: number) =>
    Math.max(0, Math.min(255, Math.round(c + amount * 255)));
  const to2 = (c: number) => adj(c).toString(16).padStart(2, "0");
  return `#${to2(r)}${to2(g)}${to2(b)}`;
}

export function ButtonSwatch({
  colorHex,
  holeType,
  material,
  size = 160,
  label,
  className,
}: Props) {
  const id = `btn-${colorHex.slice(1)}-${holeType}`;
  const light = shade(colorHex, 0.22);
  const dark = shade(colorHex, -0.28);
  const rim = shade(colorHex, -0.12);
  const isMetal = material === "metal";
  const isShell = material === "shell";

  const cx = 50;
  const cy = 50;
  const r = 42;

  // Hole geometry
  const holeR = 4.2;
  const holeFill = shade(colorHex, -0.55);
  const holeOffset = 12;

  const holes: Array<[number, number]> = [];
  if (holeType === "2-hole") {
    holes.push([cx - holeOffset, cy], [cx + holeOffset, cy]);
  } else if (holeType === "4-hole") {
    holes.push(
      [cx - holeOffset, cy - holeOffset],
      [cx + holeOffset, cy - holeOffset],
      [cx - holeOffset, cy + holeOffset],
      [cx + holeOffset, cy + holeOffset],
    );
  }

  return (
    <svg
      role="img"
      aria-label={label ?? `${material} ${holeType} button`}
      viewBox="0 0 100 100"
      width={size}
      height={size}
      className={className}
    >
      <defs>
        <radialGradient id={`${id}-face`} cx="38%" cy="32%" r="75%">
          <stop offset="0%" stopColor={light} />
          <stop offset="62%" stopColor={colorHex} />
          <stop offset="100%" stopColor={dark} />
        </radialGradient>
        {isShell && (
          <radialGradient id={`${id}-iri`} cx="65%" cy="70%" r="60%">
            <stop offset="0%" stopColor="#bfe3e0" stopOpacity="0.5" />
            <stop offset="45%" stopColor="#e9d6e8" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
          </radialGradient>
        )}
        <radialGradient id={`${id}-shadow`} cx="50%" cy="58%" r="60%">
          <stop offset="70%" stopColor="#000000" stopOpacity="0.16" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* cast shadow */}
      <ellipse cx={cx} cy={cy + 6} rx={r} ry={r * 0.94} fill={`url(#${id}-shadow)`} />

      {/* body */}
      <circle cx={cx} cy={cy} r={r} fill={rim} />
      <circle cx={cx} cy={cy} r={r - 2} fill={`url(#${id}-face)`} />

      {/* rim bevel ring */}
      <circle
        cx={cx}
        cy={cy}
        r={r - 6}
        fill="none"
        stroke={shade(colorHex, isMetal ? 0.3 : 0.12)}
        strokeWidth={1.2}
        opacity={0.7}
      />

      {isShell && <circle cx={cx} cy={cy} r={r - 2} fill={`url(#${id}-iri)`} />}

      {/* specular highlight */}
      <ellipse cx={cx - 12} cy={cy - 14} rx={10} ry={6} fill="#ffffff" opacity={isMetal ? 0.4 : 0.22} />

      {/* holes or shank */}
      {holeType === "shank" || holeType === "toggle" ? (
        <>
          <circle cx={cx} cy={cy} r={6} fill={shade(colorHex, -0.18)} opacity={0.6} />
          <circle cx={cx} cy={cy} r={2.4} fill={holeFill} />
        </>
      ) : (
        holes.map(([hx, hy], i) => (
          <g key={i}>
            <circle cx={hx} cy={hy} r={holeR + 1} fill={shade(colorHex, -0.16)} opacity={0.5} />
            <circle cx={hx} cy={hy} r={holeR} fill={holeFill} />
          </g>
        ))
      )}
    </svg>
  );
}
