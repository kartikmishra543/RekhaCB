import Image from "next/image";

/** Shared dark-surface wordmark. Screen blending removes the black canvas. */
export function BrandLogo({ className = "" }: { className?: string }) {
  return (
    <Image
      src="/rekhacb-logo.png"
      alt="RekhaCB"
      width={2172}
      height={724}
      priority
      className={`h-auto max-w-full object-contain mix-blend-screen ${className}`}
    />
  );
}
