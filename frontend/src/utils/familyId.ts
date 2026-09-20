const d: number[][] = [
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
  [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
  [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
  [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
  [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
  [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
  [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
  [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
  [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
  [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
];

const p: number[][] = [
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
  [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
  [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
  [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
  [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
  [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
  [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
  [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
];

const inv: number[] = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9];

/** Calculate Verhoeff check digit for numeric string */
export function verhoeffCheckDigit(num: string): string {
  let c = 0;
  const reversed = num.split('').reverse();
  for (let i = 0; i < reversed.length; i++) {
    c = d[c][p[(i + 1) % 8][parseInt(reversed[i], 10)]];
  }
  return String(inv[c]);
}

/** Validate numeric string with its check digit */
export function verhoeffValid(num: string): boolean {
  if (!num || !/^\d+$/.test(num)) return false;
  let c = 0;
  const reversed = num.split('').reverse();
  for (let i = 0; i < reversed.length; i++) {
    c = d[c][p[i % 8][parseInt(reversed[i], 10)]];
  }
  return c === 0;
}

/** Format raw input to standard GJ-DD-YY-SSSSSSS-C */
export function formatFamilyId(input: string): string {
  const cleaned = input.toUpperCase().replace(/[^A-Z0-9]/g, '');
  
  if (!cleaned.startsWith('GJ')) {
    return cleaned;
  }
  
  const digits = cleaned.slice(2);
  let result = 'GJ';

  if (digits.length > 0) result += '-' + digits.slice(0, 2);
  if (digits.length > 2) result += '-' + digits.slice(2, 4);
  if (digits.length > 4) result += '-' + digits.slice(4, 11);
  if (digits.length > 11) result += '-' + digits.slice(11, 12);

  return result;
}

/** Validate complete Family ID string */
export function validateFamilyId(fid: string): { isValid: boolean; error?: string } {
  if (!fid) return { isValid: false, error: 'Family ID is required' };
  
  const cleaned = fid.toUpperCase().replace(/[^A-Z0-9]/g, '');
  if (!cleaned.startsWith('GJ')) {
    return { isValid: false, error: 'Family ID must start with GJ' };
  }

  const digits = cleaned.slice(2);
  if (digits.length !== 12) {
    return { isValid: false, error: 'Family ID must have 12 numeric digits' };
  }

  if (!verhoeffValid(digits)) {
    return { isValid: false, error: 'Invalid check digit (Verhoeff verification failed)' };
  }

  return { isValid: true };
}
