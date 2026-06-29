import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

// Utility for merging Tailwind class strings. clsx handles conditionals/arrays,
// twMerge resolves conflicting Tailwind classes (e.g. "p-4 p-2" → "p-2").
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Converts a browser File object to a base64 data URL string (e.g. "data:image/jpeg;base64,...").
// Used before uploading a plant photo because the API accepts base64-encoded images, not raw files.
export async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      if (typeof reader.result === "string") {
        resolve(reader.result);
      } else {
        reject(new Error("Failed to convert file to base64"));
      }
    };
    reader.onerror = () => reject(new Error("Failed to read file"));
    reader.readAsDataURL(file);
  });
}
