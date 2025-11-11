import { useState, useEffect } from 'react';
import { parseReport, isValueGood, type ParsedTable, type TableRow } from '../utils/reportParser';
import { getMe, updateProfile } from '../api/user';

interface ReportViewerProps {
  reportText: string;
}

interface CustomReferences {
  [indicator: string]: string; // indicator name -> custom reference range
}

export function ReportViewer({ reportText }: ReportViewerProps) {
  const [parsedReport, setParsedReport] = useState(parseReport(reportText));
  const [customReferences, setCustomReferences] = useState<CustomReferences>({});
  const [editingRef, setEditingRef] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');

  // Load custom references from profile
  useEffect(() => {
    const loadReferences = async () => {
      try {
        const user = await getMe();
        if (user.profile?.customReferences) {
          setCustomReferences(user.profile.customReferences);
        }
      } catch (err) {
        console.error('Failed to load custom references:', err);
      }
    };
    loadReferences();
  }, []);

  // Re-parse report when text changes
  useEffect(() => {
    const parsed = parseReport(reportText);
    console.log('Parsed report:', parsed);
    console.log('Sections count:', parsed.sections.length);
    parsed.sections.forEach((section, idx) => {
      console.log(`Section ${idx}: "${section.title}", tables: ${section.tables?.length || 0}`);
      section.tables?.forEach((table, tIdx) => {
        console.log(`  Table ${tIdx}: ${table.rows.length} rows`);
      });
    });
    setParsedReport(parsed);
  }, [reportText]);

  const handleSaveReference = async (indicator: string, value: string) => {
    const newRefs = { ...customReferences, [indicator]: value };
    setCustomReferences(newRefs);
    setEditingRef(null);

    // Save to profile
    try {
      await updateProfile({ customReferences: newRefs });
    } catch (err) {
      console.error('Failed to save custom reference:', err);
    }
  };

  const handleDeleteReference = async (indicator: string) => {
    const newRefs = { ...customReferences };
    delete newRefs[indicator];
    setCustomReferences(newRefs);

    // Save to profile
    try {
      await updateProfile({ customReferences: newRefs });
    } catch (err) {
      console.error('Failed to delete custom reference:', err);
    }
  };

  const renderTable = (table: ParsedTable, sectionTitle: string) => {
    return (
      <div key={`table-${sectionTitle}`} style={{ marginTop: '16px', overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ background: 'rgba(255, 255, 255, 0.2)', borderBottom: '2px solid rgba(255, 255, 255, 0.3)' }}>
              <th style={{ padding: '8px', textAlign: 'left', fontWeight: '600' }}>Показатель</th>
              <th style={{ padding: '8px', textAlign: 'right', fontWeight: '600' }}>Результат</th>
              <th style={{ padding: '8px', textAlign: 'center', fontWeight: '600' }}>Ед.изм.</th>
              <th style={{ padding: '8px', textAlign: 'center', fontWeight: '600' }}>Референс</th>
              <th style={{ padding: '8px', textAlign: 'center', fontWeight: '600' }}>Флаг</th>
            </tr>
          </thead>
          <tbody>
            {table.rows.map((row, idx) => {
              // Skip empty rows
              if (!row.indicator || row.indicator.trim() === '' || row.indicator === '—') {
                return null;
              }
              
              const customRef = customReferences[row.indicator];
              const status = isValueGood(row.result, row.reference, customRef);
              const displayRef = customRef || row.reference;
              const isEditing = editingRef === row.indicator;

              return (
                <tr key={idx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
                  <td style={{ padding: '8px', fontWeight: '500' }}>{row.indicator}</td>
                  <td
                    style={{
                      padding: '8px',
                      textAlign: 'right',
                      fontWeight: '700',
                      fontSize: '14px',
                      color:
                        status === 'good'
                          ? '#22c55e' // green
                          : status === 'bad'
                          ? '#ef4444' // red
                          : 'inherit',
                      backgroundColor: status === 'bad' ? 'rgba(239, 68, 68, 0.1)' : status === 'good' ? 'rgba(34, 197, 94, 0.1)' : 'transparent',
                    }}
                  >
                    {row.result}
                  </td>
                  <td style={{ padding: '8px', textAlign: 'center', fontSize: '12px', opacity: 0.7 }}>
                    {row.unit}
                  </td>
                  <td style={{ padding: '8px', textAlign: 'center' }}>
                    {isEditing ? (
                      <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                        <input
                          type="text"
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          style={{
                            width: '80px',
                            padding: '4px',
                            fontSize: '12px',
                            borderRadius: '4px',
                            border: '1px solid rgba(255, 255, 255, 0.3)',
                            background: 'rgba(255, 255, 255, 0.2)',
                          }}
                          autoFocus
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              handleSaveReference(row.indicator, editValue);
                            } else if (e.key === 'Escape') {
                              setEditingRef(null);
                            }
                          }}
                        />
                        <button
                          onClick={() => handleSaveReference(row.indicator, editValue)}
                          style={{
                            padding: '2px 6px',
                            fontSize: '11px',
                            borderRadius: '4px',
                            border: 'none',
                            background: '#22c55e',
                            color: 'white',
                            cursor: 'pointer',
                          }}
                        >
                          ✓
                        </button>
                        <button
                          onClick={() => setEditingRef(null)}
                          style={{
                            padding: '2px 6px',
                            fontSize: '11px',
                            borderRadius: '4px',
                            border: 'none',
                            background: '#ef4444',
                            color: 'white',
                            cursor: 'pointer',
                          }}
                        >
                          ✕
                        </button>
                      </div>
                    ) : (
                      <div style={{ display: 'flex', gap: '4px', alignItems: 'center', justifyContent: 'center' }}>
                        <span style={{ fontSize: '12px' }}>{displayRef}</span>
                        {customRef && (
                          <span
                            style={{
                              fontSize: '10px',
                              opacity: 0.6,
                              cursor: 'pointer',
                            }}
                            title="Пользовательский референс"
                          >
                            ✏️
                          </span>
                        )}
                        <button
                          onClick={() => {
                            setEditingRef(row.indicator);
                            setEditValue(customRef || row.reference);
                          }}
                          style={{
                            padding: '2px 6px',
                            fontSize: '10px',
                            borderRadius: '4px',
                            border: 'none',
                            background: 'rgba(255, 255, 255, 0.2)',
                            color: 'inherit',
                            cursor: 'pointer',
                            marginLeft: '4px',
                          }}
                          title="Изменить референс"
                        >
                          ✏️
                        </button>
                        {customRef && (
                          <button
                            onClick={() => handleDeleteReference(row.indicator)}
                            style={{
                              padding: '2px 6px',
                              fontSize: '10px',
                              borderRadius: '4px',
                              border: 'none',
                              background: 'rgba(239, 68, 68, 0.3)',
                              color: 'inherit',
                              cursor: 'pointer',
                              marginLeft: '2px',
                            }}
                            title="Удалить пользовательский референс"
                          >
                            ✕
                          </button>
                        )}
                      </div>
                    )}
                  </td>
                  <td style={{ padding: '8px', textAlign: 'center' }}>
                    {status === 'good' && '✓'}
                    {status === 'bad' && '⚠'}
                    {status === 'unknown' && '—'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
      {parsedReport.sections.map((section, sectionIdx) => (
        <div key={sectionIdx} style={{ marginBottom: '24px' }}>
          <h3
            style={{
              fontSize: '18px',
              fontWeight: '600',
              marginBottom: '12px',
              color: 'var(--text-primary)',
            }}
          >
            {section.title}
          </h3>

          {section.tables && section.tables.map((table, tableIdx) => renderTable(table, `${section.title}-${tableIdx}`))}

          {section.content.trim() && (
            <div
              style={{
                whiteSpace: 'pre-wrap',
                marginTop: '12px',
                padding: '12px',
                background: 'rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
              }}
            >
              {section.content.trim()}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

