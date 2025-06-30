// LLM Log Viewer Component - UPDATED FOR NEW GENERATION_LOG SCHEMA
// Now displays generation_log table with expandable llm_data/image_data details
// Supports pagination, filtering, and detailed prompt/response viewing

import React, { useState, useEffect } from 'react';

// Helper function for API calls to generation logs
async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  return await response.json();
}

// Load generation logs with filters
async function loadGenerationLogs(filter) {
  try {
    // Build query parameters
    const params = new URLSearchParams();
    if (filter.limit) params.append('limit', filter.limit);
    if (filter.generation_type) params.append('type', filter.generation_type);
    if (filter.status) params.append('status', filter.status);
    
    const url = `http://localhost:5000/api/generation/logs?${params.toString()}`;
    const response = await apiRequest(url);
    
    if (response.success) {
      return {
        logs: response.data.logs || [],
        total: response.data.count || response.data.logs?.length || 0
      };
    } else {
      throw new Error(response.error || 'Failed to load generation logs');
    }
  } catch (error) {
    console.error('Error loading generation logs:', error);
    throw error;
  }
}

// Status Badge Component
function StatusBadge({ status }) {
  const badges = {
    'pending': 'status-pending',
    'generating': 'status-generating', 
    'completed': 'status-completed',
    'failed': 'status-failed'
  };
  
  return (
    <span className={`status-badge ${badges[status] || 'status-unknown'}`}>
      {status}
    </span>
  );
}

// Generation Type Badge Component
function GenerationTypeBadge({ type }) {
  const badges = {
    'llm': { icon: '🤖', color: 'var(--secondary-color)' },
    'image': { icon: '🎨', color: 'var(--accent-color)' }
  };
  
  const badge = badges[type] || { icon: '❓', color: 'var(--text-dim)' };
  
  return (
    <span
      style={{
        color: badge.color,
        fontWeight: 'bold',
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.3em', // optional spacing between icon and text
      }}
    >
      <span>{badge.icon}</span>
      <span>{type.toUpperCase()}</span>
    </span>
  );
}

// Expandable Row Detail Component
function LogDetailRow({ log, isExpanded, onToggle }) {
  if (!isExpanded) return null;
  
  const hasLLMData = log.generation_type === 'llm' && log.llm_data;
  const hasImageData = log.generation_type === 'image' && log.image_data;
  
  return (
    <tr className="log-detail-row">
      <td colSpan="9">
        <div className="log-detail-expanded">
          {/* Prompt Text */}
          <div className="detail-section">
            <h5>📝 Prompt Text</h5>
            <div className="code-block">
              <pre>{log.prompt_text || 'No prompt text available'}</pre>
            </div>
          </div>
          
          {/* LLM-specific details */}
          {hasLLMData && (
            <>
              <div className="detail-section">
                <h5>🤖 LLM Response</h5>
                <div className="code-block">
                  <pre>{log.llm_data.response_text || 'No response text available'}</pre>
                </div>
              </div>
              
              <div className="detail-section">
                <h5>⚙️ LLM Generation Details</h5>
                <div className="detail-grid">
                  <div><strong>Tokens:</strong> {log.llm_data.response_tokens || 'N/A'}</div>
                  <div><strong>Speed:</strong> {log.llm_data.tokens_per_second ? `${log.llm_data.tokens_per_second.toFixed(1)} tokens/sec` : 'N/A'}</div>
                  <div><strong>Temperature:</strong> {log.llm_data.temperature || 'N/A'}</div>
                  <div><strong>Max Tokens:</strong> {log.llm_data.max_tokens || 'N/A'}</div>
                  <div><strong>Parse Success:</strong> {log.llm_data.parse_success ? '✅ Yes' : '❌ No'}</div>
                  <div><strong>Has Parsed Data:</strong> {log.llm_data.has_parsed_data ? '✅ Yes' : '❌ No'}</div>
                </div>
              </div>
              
              {log.llm_data.parsed_data && (
                <div className="detail-section">
                  <h5>✅ Parsed Data</h5>
                  <div className="code-block">
                    <pre>{JSON.stringify(log.llm_data.parsed_data, null, 2)}</pre>
                  </div>
                </div>
              )}
              
              {log.llm_data.parse_error && (
                <div className="detail-section error">
                  <h5>❌ Parse Error</h5>
                  <div className="error-block">
                    <pre>{log.llm_data.parse_error}</pre>
                  </div>
                </div>
              )}
            </>
          )}
          
          {/* Image-specific details */}
          {hasImageData && (
            <div className="detail-section">
              <h5>🎨 Image Generation Details</h5>
              <div className="detail-grid">
                <div><strong>Image Path:</strong> {log.image_data.image_path || 'N/A'}</div>
                <div><strong>Has Image:</strong> {log.image_data.has_image ? '✅ Yes' : '❌ No'}</div>
                <div><strong>Generation Time:</strong> {log.image_data.generation_time ? `${log.image_data.generation_time.toFixed(1)}s` : 'N/A'}</div>
              </div>
            </div>
          )}
          
          {/* Error message if any */}
          {log.error_message && (
            <div className="detail-section error">
              <h5>❌ Generation Error</h5>
              <div className="error-block">
                <pre>{log.error_message}</pre>
              </div>
            </div>
          )}
          
          {/* Raw data for debugging */}
          <details className="raw-data-section">
            <summary>🔍 Raw Log Data (Debug)</summary>
            <div className="code-block">
              <pre>{JSON.stringify(log, null, 2)}</pre>
            </div>
          </details>
        </div>
      </td>
    </tr>
  );
}

// Main table row component
function LogTableRow({ log, isExpanded, onToggleExpand }) {
  const formatDate = (dateString) => new Date(dateString).toLocaleString();
  const formatDuration = (seconds) => seconds ? `${seconds.toFixed(1)}s` : 'N/A';
  
  return (
    <>
      <tr 
        className={`log-table-row ${isExpanded ? 'expanded' : ''}`}
        onClick={() => onToggleExpand(log.id)}
      >
        <td>{log.id}</td>
        <td><GenerationTypeBadge type={log.generation_type} /></td>
        <td>{log.prompt_type}</td>
        <td>{log.prompt_name}</td>
        <td><StatusBadge status={log.status} /></td>
        <td>{log.priority}</td>
        <td>{formatDuration(log.duration_seconds)}</td>
        <td>{log.attempts_used}/{log.max_attempts}</td>
        <td>{log.is_completed ? '✅' : '⏳'}</td>
      </tr>
      <LogDetailRow 
        log={log} 
        isExpanded={isExpanded} 
        onToggle={() => onToggleExpand(log.id)} 
      />
    </>
  );
}

// Filter Controls Component
function FilterControls({ filter, onFilterChange, onRefresh, loading }) {
  return (
    <div className="log-filters">
      <h4>🔍 Filter Generation Logs</h4>
      <div className="filter-controls">
        <select 
          value={filter.generation_type} 
          onChange={(e) => onFilterChange({...filter, generation_type: e.target.value})}
        >
          <option value="">All Types</option>
          <option value="llm">🤖 LLM Generation</option>
          <option value="image">🎨 Image Generation</option>
        </select>
        
        <select 
          value={filter.status}
          onChange={(e) => onFilterChange({...filter, status: e.target.value})}
        >
          <option value="">All Status</option>
          <option value="pending">⏳ Pending</option>
          <option value="generating">🔄 Generating</option>
          <option value="completed">✅ Completed</option>
          <option value="failed">❌ Failed</option>
        </select>
        
        <select 
          value={filter.limit}
          onChange={(e) => onFilterChange({...filter, limit: parseInt(e.target.value)})}
        >
          <option value="10">10 logs</option>
          <option value="25">25 logs</option>
          <option value="50">50 logs</option>
          <option value="100">100 logs</option>
        </select>
        
        <button 
          onClick={onRefresh} 
          disabled={loading}
          className="btn btn-secondary"
        >
          {loading ? '🔄 Loading...' : '🔄 Refresh'}
        </button>
      </div>
    </div>
  );
}

// Statistics Component
function LogStatistics({ logs }) {
  const stats = {
    total: logs.length,
    completed: logs.filter(log => log.is_completed).length,
    failed: logs.filter(log => log.is_failed).length,
    llm: logs.filter(log => log.generation_type === 'llm').length,
    image: logs.filter(log => log.generation_type === 'image').length,
    avgDuration: logs.filter(log => log.duration_seconds).reduce((sum, log) => sum + log.duration_seconds, 0) / logs.filter(log => log.duration_seconds).length || 0
  };
  
  return (
    <div className="llm-overview">
      <h3>📊 Generation Log Statistics</h3>
      <div className="grid-auto-fit grid-auto-fit-md">
        <div className="card">
          <h4>📋 Overview</h4>
          <p><strong>Total Logs:</strong> {stats.total}</p>
          <p><strong>Completed:</strong> {stats.completed} ({((stats.completed / stats.total) * 100).toFixed(1)}%)</p>
          <p><strong>Failed:</strong> {stats.failed} ({((stats.failed / stats.total) * 100).toFixed(1)}%)</p>
          <p><strong>Avg Duration:</strong> {stats.avgDuration.toFixed(1)}s</p>
        </div>
        
        <div className="card">
          <h4>🎯 By Type</h4>
          <p><strong>🤖 LLM Generations:</strong> {stats.llm}</p>
          <p><strong>🎨 Image Generations:</strong> {stats.image}</p>
          <p><strong>📊 LLM Ratio:</strong> {((stats.llm / stats.total) * 100).toFixed(1)}%</p>
          <p><strong>🎨 Image Ratio:</strong> {((stats.image / stats.total) * 100).toFixed(1)}%</p>
        </div>
      </div>
    </div>
  );
}

// Main LLM Log Viewer Component
function LLMLogViewer() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedRows, setExpandedRows] = useState(new Set());
  const [filter, setFilter] = useState({
    limit: 25,
    generation_type: '',
    status: ''
  });

  // Load data on component mount and filter changes
  useEffect(() => {
    loadAllData();
  }, [filter]);

  const loadAllData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const { logs } = await loadGenerationLogs(filter);
      setLogs(logs);
    } catch (err) {
      setError(err.message);
    }
    
    setLoading(false);
  };

  const toggleRowExpansion = (logId) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(logId)) {
      newExpanded.delete(logId);
    } else {
      newExpanded.add(logId);
    }
    setExpandedRows(newExpanded);
  };

  if (loading) {
    return (
      <div className="llm-log-viewer">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p className="loading-text">Loading generation logs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="llm-log-viewer">
      {/* Statistics Overview */}
      {logs.length > 0 && <LogStatistics logs={logs} />}

      {/* Filter Controls */}
      <FilterControls 
        filter={filter}
        onFilterChange={setFilter}
        onRefresh={loadAllData}
        loading={loading}
      />

      {error && (
        <div className="alert alert-error">
          <h4>❌ Error</h4>
          <p>{error}</p>
        </div>
      )}

      {/* Logs Table */}
      <div className="logs-section">
        <h4>📋 Generation Logs ({logs.length} {filter.limit && logs.length === filter.limit ? `of ${filter.limit}` : 'total'})</h4>
        
        {logs.length === 0 ? (
          <div className="no-logs">
            <p>No generation logs found. Try generating a monster or adjusting filters!</p>
          </div>
        ) : (
          <div className="logs-table">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Type</th>
                  <th>Prompt Type</th>
                  <th>Prompt Name</th>
                  <th>Status</th>
                  <th>Priority</th>
                  <th>Duration</th>
                  <th>Attempts</th>
                  <th>Completed</th>
                </tr>
              </thead>
              <tbody>
                {logs.map(log => (
                  <LogTableRow
                    key={log.id}
                    log={log}
                    isExpanded={expandedRows.has(log.id)}
                    onToggleExpand={toggleRowExpansion}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination Info */}
      <div className="pagination-info">
        <p>
          💡 <strong>Pagination:</strong> Showing up to {filter.limit} logs. 
          {logs.length === filter.limit && (
            <span> There may be more logs available - increase the limit or add filtering to see specific logs.</span>
          )}
        </p>
        <p>
          🔄 <strong>Future:</strong> Page navigation will be added when backend offset support is ready.
        </p>
      </div>
    </div>
  );
}

export default LLMLogViewer;