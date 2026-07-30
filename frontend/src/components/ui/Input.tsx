import { forwardRef, InputHTMLAttributes } from "react";
import { cn } from "@/utils/cn";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");
    return (
      <div className="space-y-1.5">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-foreground">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            "block w-full rounded-lg border border-input bg-background px-3.5 py-2.5 text-base sm:text-sm text-foreground shadow-sm",
            "placeholder:text-muted-foreground",
            "focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all duration-200",
            "disabled:bg-muted disabled:text-muted-foreground disabled:cursor-not-allowed",
            error && "border-destructive focus:border-destructive focus:ring-destructive/20",
            className
          )}
          {...props}
        />
        {error && <p className="text-xs text-destructive animate-in fade-in slide-in-from-top-1 duration-150">{error}</p>}
      </div>
    );
  }
);
Input.displayName = "Input";
