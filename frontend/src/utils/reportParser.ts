// Utility to parse analysis report and determine value status

export interface TableRow {
  indicator: string;
  result: string;
  unit: string;
  reference: string;
  flag: string;
}

export interface ParsedTable {
  title: string;
  rows: TableRow[];
}

export interface ParsedReport {
  sections: {
    title: string;
    content: string;
    tables?: ParsedTable[];
  }[];
}

// Parse markdown table
function parseTable(tableText: string): ParsedTable | null {
  const lines = tableText.trim().split('\n');
  if (lines.length < 3) return null;

  // Find header row (usually line 1 or 2)
  let headerIndex = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('|') && lines[i].includes('Показатель')) {
      headerIndex = i;
      break;
    }
  }
  if (headerIndex === -1) return null;

  // Skip separator row (usually after header)
  const dataStartIndex = headerIndex + 2;

  const rows: TableRow[] = [];
  for (let i = dataStartIndex; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line || !line.includes('|')) continue;
    // Skip separator rows (usually contain only dashes and pipes)
    if (line.match(/^[\s|:\-]+$/)) continue;
    if (line.startsWith('**') || line.startsWith('###') || line.startsWith('##')) break; // End of table

    const cells = line.split('|').map(c => c.trim()).filter(c => c && c !== '');
    // Need at least indicator, result, and reference
    if (cells.length >= 3) {
      const row: TableRow = {
        indicator: cells[0] || '',
        result: cells[1] || '',
        unit: cells[2] || '',
        reference: cells[3] || '',
        flag: cells[4] || '',
      };
      
      // Only add if indicator is not empty
      if (row.indicator && row.indicator !== '—' && row.indicator !== 'Показатель') {
        rows.push(row);
      }
    }
  }

  return rows.length > 0 ? { title: '', rows } : null;
}

// Parse reference range (e.g., "120-160", "3,5-5,1", "< 5.0", "> 10")
function parseReferenceRange(reference: string): { min?: number; max?: number } | null {
  if (!reference || reference === '—' || reference.trim() === '') return null;

  const ref = reference.trim();
  
  // Range format: "120-160" or "3,5-5,1" or "120 - 160" (handles both comma and dot)
  const rangeMatch = ref.match(/(\d+[,.]?\d*)\s*-\s*(\d+[,.]?\d*)/);
  if (rangeMatch) {
    const min = parseFloat(rangeMatch[1].replace(',', '.'));
    const max = parseFloat(rangeMatch[2].replace(',', '.'));
    if (!isNaN(min) && !isNaN(max)) {
      return { min, max };
    }
  }

  // Less than: "< 5.0" or "<5,0"
  const lessMatch = ref.match(/<\s*(\d+[,.]?\d*)/);
  if (lessMatch) {
    const max = parseFloat(lessMatch[1].replace(',', '.'));
    if (!isNaN(max)) {
      return { max };
    }
  }

  // Greater than: "> 10" or ">10"
  const greaterMatch = ref.match(/>\s*(\d+[,.]?\d*)/);
  if (greaterMatch) {
    const min = parseFloat(greaterMatch[1].replace(',', '.'));
    if (!isNaN(min)) {
      return { min };
    }
  }

  // Single value: "5.0" or "5,0" (treat as exact or range with small tolerance)
  const singleMatch = ref.match(/^(\d+[,.]?\d*)$/);
  if (singleMatch) {
    const value = parseFloat(singleMatch[1].replace(',', '.'));
    if (!isNaN(value)) {
      return {
        min: value * 0.95, // 5% tolerance
        max: value * 1.05,
      };
    }
  }

  return null;
}

// Helper to parse number from string (handles both comma and dot as decimal separator)
function parseNumber(str: string): number | null {
  if (!str || str === '—' || str.trim() === '') return null;
  
  // Remove all non-digit characters except comma, dot, and minus
  let cleaned = str.replace(/[^\d.,-]/g, '');
  
  // Replace comma with dot for parsing
  cleaned = cleaned.replace(',', '.');
  
  // Handle cases like "4,78 х10^12/л" - extract just the number part
  const match = cleaned.match(/(-?\d+\.?\d*)/);
  if (match) {
    const num = parseFloat(match[1]);
    return isNaN(num) ? null : num;
  }
  
  return null;
}

// Check if value is within reference range
export function isValueGood(result: string, reference: string, customReference?: string): 'good' | 'bad' | 'unknown' {
  const refToUse = customReference || reference;
  if (!refToUse || refToUse === '—' || refToUse.trim() === '') return 'unknown';
  if (!result || result === '—' || result.trim() === '') return 'unknown';

  const numResult = parseNumber(result);
  if (numResult === null) return 'unknown';

  const range = parseReferenceRange(refToUse);
  if (!range) return 'unknown';

  if (range.min !== undefined && range.max !== undefined) {
    return numResult >= range.min && numResult <= range.max ? 'good' : 'bad';
  } else if (range.min !== undefined) {
    return numResult >= range.min ? 'good' : 'bad';
  } else if (range.max !== undefined) {
    return numResult <= range.max ? 'good' : 'bad';
  }

  return 'unknown';
}

// Parse markdown report into structured format
export function parseReport(reportText: string): ParsedReport {
  const sections: ParsedReport['sections'] = [];
  const lines = reportText.split('\n');

  let currentSection: { title: string; content: string; tables?: ParsedTable[] } | null = null;
  let currentTable: string[] = [];
  let inTable = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Check for section header (## or ###)
    if (line.startsWith('##')) {
      // Save previous section
      if (currentSection) {
        // Try to parse any accumulated table
        if (currentTable.length > 0) {
          const table = parseTable(currentTable.join('\n'));
          if (table) {
            if (!currentSection.tables) currentSection.tables = [];
            currentSection.tables.push(table);
          }
          currentTable = [];
        }
        sections.push(currentSection);
      }

      // Start new section
      const title = line.replace(/^#+\s*/, '').trim();
      currentSection = { title, content: '' };
      inTable = false;
      continue;
    }

    // Check if line is part of a table
    if (line.includes('|') && line.includes('Показатель')) {
      inTable = true;
      currentTable = [line];
      continue;
    }

    if (inTable) {
      if (line.includes('|')) {
        currentTable.push(line);
      } else {
        // End of table
        if (currentTable.length > 0 && currentSection) {
          const table = parseTable(currentTable.join('\n'));
          if (table) {
            if (!currentSection.tables) currentSection.tables = [];
            currentSection.tables.push(table);
          }
          currentTable = [];
        }
        inTable = false;
        if (currentSection && line.trim()) {
          currentSection.content += line + '\n';
        }
      }
    } else {
      if (currentSection) {
        currentSection.content += line + '\n';
      }
    }
  }

  // Save last section
  if (currentSection) {
    if (currentTable.length > 0) {
      const table = parseTable(currentTable.join('\n'));
      if (table) {
        if (!currentSection.tables) currentSection.tables = [];
        currentSection.tables.push(table);
      }
    }
    sections.push(currentSection);
  }

  return { sections };
}

