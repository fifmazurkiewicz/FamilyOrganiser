import { cn } from "@/utils/cn";

interface ProgressProps {
  value: number;
  max?: number;
  className?: string;
  indicatorClassName?: string;
  showLabel?: boolean;
}

export function Progress({ value, max = 100, className, indicatorClassName, showLabel }: ProgressProps) {
  const percent = Math.min(100, (value / max) * 100);
  return (
    <div className={cn("relative h-2 w-full overflow-hidden rounded-full bg-gray-100", className)}>
      <div
        className={cn(
          "h-full rounded-full bg-primary transition-all duration-300",
          percent > 90 && "bg-red-500",
          percent > 75 && percent <= 90 && "bg-amber-500",
          indicatorClassName
        )}
        style={{ width: `${percent}%` }}
      />
      {showLabel && (
        <span className="absolute right-0 top-3 text-xs text-gray-500">{Math.round(percent)}%</span>
      )}
    </div>
  );
}
