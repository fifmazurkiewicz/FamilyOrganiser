import { forwardRef, ButtonHTMLAttributes } from "react";
import { cn } from "@/utils/cn";

type Variant = "primary" | "secondary" | "ghost" | "danger" | "outline";
type Size = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

const variantClasses: Record<Variant, string> = {
  primary:
    "bg-primary text-white hover:bg-primary-dark focus-visible:ring-primary shadow-sm shadow-primary/20 hover:shadow-md hover:shadow-primary/30",
  secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:ring-gray-300",
  ghost: "hover:bg-gray-100 text-gray-700 focus-visible:ring-gray-300",
  danger: "bg-destructive text-white hover:bg-red-700 focus-visible:ring-destructive shadow-sm shadow-red-500/20",
  outline: "border border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-gray-400 focus-visible:ring-gray-300",
};

const sizeClasses: Record<Size, string> = {
  sm: "h-8 px-3 text-xs rounded-lg",
  md: "h-9 px-4 text-sm rounded-lg",
  lg: "h-11 px-6 text-base rounded-xl",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", size = "md", loading, className, children, disabled, ...props }, ref) => (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={cn(
        "inline-flex items-center justify-center gap-2 font-semibold transition-all duration-200",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
        "disabled:pointer-events-none disabled:opacity-50",
        "active:scale-[0.97]",
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      {...props}
    >
      {loading && (
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      )}
      {children}
    </button>
  )
);
Button.displayName = "Button";