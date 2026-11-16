import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import type { ButtonHTMLAttributes, HTMLAttributes, ReactNode } from "react";

const buttonStyles = cva(
  "inline-flex items-center justify-center gap-2 rounded-lg text-sm font-medium h-9 px-3 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-primary text-primary-foreground hover:opacity-90",
        secondary: "bg-card text-foreground border border-border",
        ghost: "bg-transparent text-foreground hover:bg-muted",
      },
    },
    defaultVariants: { variant: "primary" },
  },
);

export function Button({
  className,
  variant,
  asChild,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & VariantProps<typeof buttonStyles> & { asChild?: boolean }) {
  const Comp = asChild ? Slot : "button";
  return <Comp className={cn(buttonStyles({ variant }), className)} {...props} />;
}

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("rounded-lg border border-border bg-card text-card-foreground", className)} {...props} />;
}

const riskText: Record<string, string> = {
  critical: "text-[var(--risk-critical)] bg-[color-mix(in_oklch,var(--risk-critical)_15%,transparent)]",
  high: "text-[var(--risk-high)] bg-[color-mix(in_oklch,var(--risk-high)_15%,transparent)]",
  medium: "text-[var(--risk-medium)] bg-[color-mix(in_oklch,var(--risk-medium)_15%,transparent)]",
  low: "text-[var(--risk-low)] bg-[color-mix(in_oklch,var(--risk-low)_15%,transparent)]",
};

export function RiskChip({ level }: { level: string }) {
  const label = level.slice(0, 1).toUpperCase() + level.slice(1);
  return (
    <span className={cn("inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium", riskText[level] ?? riskText.low)}>
      <span className="size-1.5 rounded-full bg-current" aria-hidden />
      {label}
    </span>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-md bg-muted", className)} />;
}

export function Empty({ title, action }: { title: string; action?: ReactNode }) {
  return (
    <Card className="p-8 text-sm text-muted-foreground">
      <p>{title}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </Card>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <Card className="p-6">
      <p className="text-sm">{message}</p>
      {onRetry ? (
        <Button className="mt-4" variant="secondary" onClick={onRetry}>
          Retry
        </Button>
      ) : null}
    </Card>
  );
}
