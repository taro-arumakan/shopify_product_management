/**
 * Hammond Button Works logo, rebuilt as crisp inline SVG (scales to any size,
 * inherits `currentColor`).
 *
 * NOTE: the "hammond" wordmark in the supplied artwork is a *custom* rounded
 * geometric typeface. This recreates its character with a geometric font stack
 * plus the brand's dot-in-`o` accent and the serif "BUTTON WORKS" lockup — a
 * faithful approximation, not a pixel trace. For a pixel-perfect mark, drop the
 * original vector (AI/SVG) or font file in and swap the <text>/paths here.
 *
 * Variants:
 *  - "compact": wordmark only (header)
 *  - "full":    framed lockup — wordmark + BUTTON WORKS in the double-line frame
 *  - "stamp":   circular "·BUTTON WORKS· MADE IN JAPAN" maker's mark (footer)
 */

const GEOMETRIC =
  'Futura, "Century Gothic", "Trebuchet MS", "Avant Garde", system-ui, sans-serif';

type Variant = "compact" | "full" | "stamp";

export function Logo({
  variant = "full",
  className,
}: {
  variant?: Variant;
  className?: string;
}) {
  if (variant === "stamp") return <Stamp className={className} />;
  if (variant === "full") return <Full className={className} />;
  return <Wordmark className={className} />;
}

/** The "hammond" wordmark with a filled brass dot inside the `o`. */
function Wordmark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 252 52"
      className={className}
      role="img"
      aria-label="hammond"
      fill="none"
    >
      <text
        x="0"
        y="40"
        fontSize="46"
        fill="currentColor"
        style={{
          fontFamily: GEOMETRIC,
          fontWeight: 500,
          letterSpacing: "-0.015em",
        }}
      >
        hammond
      </text>
      {/* dot-in-o brand accent (sits over the 'o' of hammond) */}
      <circle cx="178" cy="27" r="5.2" fill="var(--color-accent, #8a6d3b)" />
    </svg>
  );
}

/** Framed lockup for the home hero. */
function Full({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 300 150"
      className={className}
      role="img"
      aria-label="Hammond Button Works"
      fill="none"
    >
      {/* double-line frame */}
      <rect x="6" y="6" width="288" height="138" stroke="currentColor" strokeWidth="1.6" />
      <rect x="11" y="11" width="278" height="128" stroke="currentColor" strokeWidth="0.8" />

      <text
        x="150"
        y="78"
        textAnchor="middle"
        fontSize="50"
        fill="currentColor"
        style={{ fontFamily: GEOMETRIC, fontWeight: 500, letterSpacing: "-0.015em" }}
      >
        hammond
      </text>
      <circle cx="196" cy="62" r="5.6" fill="var(--color-accent, #8a6d3b)" />

      <text
        x="150"
        y="112"
        textAnchor="middle"
        fontSize="26"
        fill="currentColor"
        style={{
          fontFamily: 'var(--font-display, ui-serif, Georgia, serif)',
          letterSpacing: "0.18em",
        }}
      >
        BUTTON WORKS
      </text>
    </svg>
  );
}

/** Circular maker's stamp echoing the Instagram badge. */
function Stamp({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 100 100"
      className={className}
      role="img"
      aria-label="Hammond Button Works — Made in Japan"
      fill="none"
    >
      <defs>
        <path id="hbw-top" d="M 21,52 A 29,29 0 0 1 79,52" />
        <path id="hbw-bot" d="M 23,52 A 27,27 0 0 0 77,52" />
      </defs>
      <circle cx="50" cy="50" r="47" stroke="currentColor" strokeWidth="1.4" />
      <circle cx="50" cy="50" r="42.5" stroke="currentColor" strokeWidth="0.7" />

      <text
        fill="currentColor"
        fontSize="9"
        style={{ fontFamily: GEOMETRIC, letterSpacing: "0.16em" }}
      >
        <textPath href="#hbw-top" startOffset="50%" textAnchor="middle">
          BUTTON WORKS
        </textPath>
      </text>
      <text
        fill="currentColor"
        fontSize="7.5"
        style={{ fontFamily: GEOMETRIC, letterSpacing: "0.14em" }}
      >
        <textPath href="#hbw-bot" startOffset="50%" textAnchor="middle">
          MADE IN JAPAN
        </textPath>
      </text>

      {/* center sew-button motif */}
      <circle cx="50" cy="50" r="13" stroke="currentColor" strokeWidth="1.2" />
      <circle cx="50" cy="50" r="9.5" stroke="currentColor" strokeWidth="0.6" />
      <circle cx="46" cy="50" r="1.5" fill="currentColor" />
      <circle cx="54" cy="50" r="1.5" fill="currentColor" />
    </svg>
  );
}
