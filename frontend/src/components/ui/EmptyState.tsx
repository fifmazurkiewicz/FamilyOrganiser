import { LucideIcon } from "lucide-react";
import { Button } from "./Button";
import { cn } from "@/utils/cn";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  action?: { label: string; onClick: () => void };
  className?: string;
}

export function EmptyState({ icon: Icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-16 text-center animate-in fade-in zoom-in-95 duration-300", className)}>
      <div className="mb-5 rounded-2xl bg-gradient-to-br from-primary-light to-accent p-4 ring-1 ring-primary/10">
        <Icon className="h-10 w-10 text-primary" />
      </div>
      <h3 className="mb-1.5 text-lg font-semibold text-gray-900">{title}</h3>
      {description && <p className="mb-5 text-sm text-gray-500 max-w-xs">{description}</p>}
      {action && (
        <Button onClick={action.onClick} size="md">
          {action.label}
        </Button>
      )}
    </div>
  );
}