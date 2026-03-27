/**
 * Returns the Dong-Haeng Bokgwon color for a lotto number per D-06.
 *
 * Color bands:
 *   1-10  → yellow (#ffc107)
 *   11-20 → blue   (#2196f3)
 *   21-30 → red    (#f44336)
 *   31-40 → gray   (#9e9e9e)
 *   41-45 → green  (#4caf50)
 */
export function getLottoBallColor(num: number): string {
  if (num >= 1 && num <= 10) return '#ffc107';
  if (num >= 11 && num <= 20) return '#2196f3';
  if (num >= 21 && num <= 30) return '#f44336';
  if (num >= 31 && num <= 40) return '#9e9e9e';
  if (num >= 41 && num <= 45) return '#4caf50';
  return '#9e9e9e'; // fallback
}

/**
 * Formats a lotto number as a zero-padded 2-digit string per D-07.
 */
export function formatNumber(num: number): string {
  return num.toString().padStart(2, '0');
}
