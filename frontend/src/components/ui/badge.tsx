import React from "react";
import { cn } from "@/lib/utils";

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {}

export const Badge = ({ className, children, ...props }: BadgeProps) => {
  if (!children) return null; // avoid rendering empty badge

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full bg-muted px-2.5 py-0.5 text-sm font-medium",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
