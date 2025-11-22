/**
 * SROIE Dataset Helper Utilities for E2E Tests
 * 
 * These utilities help load and validate ground truth data from the SROIE dataset
 * and compare extracted results with expected values.
 */

import { readFileSync, existsSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export interface SROIEGroundTruth {
  company: string;
  date: string;
  address: string;
  total: string;
}

export interface SROIETestFile {
  imagePath: string;
  groundTruthPath: string;
  groundTruth: SROIEGroundTruth;
  fileId: string;
}

/**
 * Normalize text for comparison (similar to backend sroie_utils.normalize_text)
 */
export function normalizeText(text: string | null | undefined): string {
  if (!text) return '';
  
  return text
    .toString()
    .replace(/[\t\n]/g, ' ')  // Replace tabs and newlines with space
    .replace(/\s+/g, ' ')      // Replace multiple spaces with single space
    .trim()
    .toLowerCase();
}

/**
 * Normalize date for comparison
 */
export function normalizeDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '';
  
  // Remove common date separators and normalize format
  return dateStr
    .toString()
    .replace(/[-\/]/g, '/')
    .trim()
    .toLowerCase();
}

/**
 * Normalize amount for comparison
 */
export function normalizeAmount(amount: number | string | null | undefined): number {
  if (amount === null || amount === undefined) return 0;
  
  if (typeof amount === 'number') {
    return Math.round(amount * 100) / 100; // Round to 2 decimal places
  }
  
  // Parse string amount
  const parsed = parseFloat(amount.toString().replace(/[^\d.-]/g, ''));
  return isNaN(parsed) ? 0 : Math.round(parsed * 100) / 100;
}

/**
 * Find available SROIE test files
 */
export function findSROIETestFiles(): SROIETestFile[] {
  const SROIE_DATA_DIR = path.join(__dirname, '../../../docs/datasets/SROIE_GitHub/data');
  const SROIE_IMG_DIR = path.join(SROIE_DATA_DIR, 'img');
  const SROIE_KEY_DIR = path.join(SROIE_DATA_DIR, 'key');
  
  const testFiles: SROIETestFile[] = [];
  
  // Try common test invoice IDs
  const testInvoiceIds = ['001', '002', '003', '005', '010', '020', '050', '100'];
  
  for (const invoiceId of testInvoiceIds) {
    const imagePath = path.join(SROIE_IMG_DIR, `${invoiceId}.jpg`);
    const groundTruthPath = path.join(SROIE_KEY_DIR, `${invoiceId}.json`);
    
    if (existsSync(imagePath) && existsSync(groundTruthPath)) {
      try {
        const groundTruthJson = readFileSync(groundTruthPath, 'utf-8');
        const groundTruth = JSON.parse(groundTruthJson) as SROIEGroundTruth;
        
        testFiles.push({
          imagePath,
          groundTruthPath,
          groundTruth,
          fileId: invoiceId
        });
      } catch (error) {
        console.warn(`Failed to load ground truth for ${invoiceId}:`, error);
      }
    }
  }
  
  return testFiles;
}

/**
 * Get the first available SROIE test file
 */
export function getFirstSROIETestFile(): SROIETestFile | null {
  const testFiles = findSROIETestFiles();
  return testFiles.length > 0 ? testFiles[0] : null;
}

/**
 * Compare extracted data with ground truth
 */
export interface ComparisonResult {
  matches: boolean;
  details: {
    company?: { match: boolean; extracted: string; expected: string };
    date?: { match: boolean; extracted: string; expected: string };
    total?: { match: boolean; extracted: number; expected: number; tolerance?: number };
    address?: { match: boolean; extracted: string; expected: string };
  };
}

export function compareWithGroundTruth(
  extracted: {
    vendor?: string;
    invoice_date?: string;
    amount?: number | string;
    address?: string;
  },
  groundTruth: SROIEGroundTruth,
  options: {
    amountTolerance?: number; // Default 0.01 (1 cent)
    fuzzyMatch?: boolean; // Use fuzzy matching for text
  } = {}
): ComparisonResult {
  const { amountTolerance = 0.01, fuzzyMatch = true } = options;
  
  const details: ComparisonResult['details'] = {};
  let allMatch = true;
  
  // Compare company/vendor
  if (extracted.vendor !== undefined) {
    const extractedNorm = normalizeText(extracted.vendor);
    const expectedNorm = normalizeText(groundTruth.company);
    
    let match = false;
    if (fuzzyMatch) {
      // Fuzzy match: check if one contains the other or similarity > 0.7
      match = extractedNorm.includes(expectedNorm) || 
              expectedNorm.includes(extractedNorm) ||
              similarity(extractedNorm, expectedNorm) > 0.7;
    } else {
      match = extractedNorm === expectedNorm;
    }
    
    details.company = {
      match,
      extracted: extracted.vendor,
      expected: groundTruth.company
    };
    
    if (!match) allMatch = false;
  }
  
  // Compare date
  if (extracted.invoice_date !== undefined) {
    const extractedNorm = normalizeDate(extracted.invoice_date);
    const expectedNorm = normalizeDate(groundTruth.date);
    
    // Date matching is more lenient - check if dates are similar
    const match = extractedNorm === expectedNorm || 
                  similarity(extractedNorm, expectedNorm) > 0.8;
    
    details.date = {
      match,
      extracted: extracted.invoice_date,
      expected: groundTruth.date
    };
    
    if (!match) allMatch = false;
  }
  
  // Compare total amount
  if (extracted.amount !== undefined) {
    const extractedAmount = normalizeAmount(extracted.amount);
    const expectedAmount = normalizeAmount(groundTruth.total);
    const diff = Math.abs(extractedAmount - expectedAmount);
    
    const match = diff <= amountTolerance;
    
    details.total = {
      match,
      extracted: extractedAmount,
      expected: expectedAmount,
      tolerance: amountTolerance
    };
    
    if (!match) allMatch = false;
  }
  
  // Compare address (optional, often not extracted)
  if (extracted.address !== undefined && groundTruth.address) {
    const extractedNorm = normalizeText(extracted.address);
    const expectedNorm = normalizeText(groundTruth.address);
    
    const match = fuzzyMatch 
      ? similarity(extractedNorm, expectedNorm) > 0.6
      : extractedNorm === expectedNorm;
    
    details.address = {
      match,
      extracted: extracted.address,
      expected: groundTruth.address
    };
    
    // Address mismatch doesn't fail the test (it's often not extracted)
  }
  
  return {
    matches: allMatch,
    details
  };
}

/**
 * Calculate similarity between two strings (0-1)
 * Uses a simple character-based similarity metric
 */
function similarity(str1: string, str2: string): number {
  if (str1 === str2) return 1.0;
  if (str1.length === 0 || str2.length === 0) return 0.0;
  
  // Simple character overlap similarity
  const longer = str1.length > str2.length ? str1 : str2;
  const shorter = str1.length > str2.length ? str2 : str1;
  
  if (longer.length === 0) return 1.0;
  
  // Count matching characters
  let matches = 0;
  for (let i = 0; i < shorter.length; i++) {
    if (longer.includes(shorter[i])) {
      matches++;
    }
  }
  
  return matches / longer.length;
}

