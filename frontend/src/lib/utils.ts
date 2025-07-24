// Utility Functions
// Common helper functions used throughout the app.

// Import clsx for className logic and tailwind-merge for Tailwind class merging
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

// Combines CSS classes intelligently using clsx and tailwind-merge
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
