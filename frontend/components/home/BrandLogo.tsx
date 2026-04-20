import Image from "next/image";
import Link from "next/link";

type BrandLogoProps = {
  className?: string;
  textClassName?: string;
  iconSize?: number;
  /** Smaller mark + wordmark for dense headers (e.g. questionnaire, mobile). */
  compact?: boolean;
  /** Link target (default marketing home `/`). */
  href?: string;
};

export function BrandLogo({
  className = "",
  textClassName = "font-medium text-[#1B3A5C]",
  iconSize,
  compact = false,
  href = "/",
}: BrandLogoProps) {
  const resolvedIcon = iconSize ?? (compact ? 28 : 38);
  const titleClass = compact
    ? "text-lg leading-6 tracking-[-0.35px]"
    : "text-2xl leading-7 tracking-[-0.5px]";

  return (
    <Link
      href={href}
      className={`inline-flex items-center gap-1 ${compact ? "gap-1" : "gap-1.5"} ${className}`}
    >
      <Image
        src="/dent-trimmed.png"
        alt=""
        width={resolvedIcon * 2}
        height={resolvedIcon * 2}
        className="shrink-0 object-contain"
        style={{ width: resolvedIcon, height: resolvedIcon }}
        priority
      />
      <span className={`${titleClass} ${textClassName}`}>
        DentNav
      </span>
    </Link>
  );
}
