// LLM Log Viewer Component
// Displays LLM generation logs for debugging and monitoring
// Shows prompts, responses, timing, and parsing results

import React, { useState, useEffect } from 'react';
import { getLLMLogs, getLLMLogDetail, getLLMStatus, getLLMStats } from '../../services/api';

function LLMLogViewer() {
  const [logs, setLogs] = useState([]);
  const [selectedLog, setSelectedLog] = useState(null);
  const [llmStatus, setLLMStatus] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState({
    limit: 20,
    status: '',
    prompt_type: ''
  });

  // Load data on component mount
  useEffect(() => {
    loadAllData();
  }, [filter]);

  const loadAllData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [logsResponse, statusResponse, statsResponse] = await Promise.all([
        getLLMLogs(filter),
        getLLMStatus(),
        getLLMStats()
      ]);
      
      if (logsResponse.success) {
        setLogs(logsResponse.data.logs);
      }
      
      if (statusResponse.success) {
        setLLMStatus(statusResponse.data);
      }
      
      if (statsResponse.success) {
        setStats(statsResponse.data);
      }
      
    } catch (err) {
      setError(err.message);
    }
    
    setLoading(false);
  };

  const handleLogClick = async (logId) => {
    try {
      const response = await getLLMLogDetail(logId);
      if (response.success) {
        setSelectedLog(response.data);
      }
    } catch (err) {
      setError(`Failed to load log details: ${err.message}`);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (seconds) => {
    return seconds ? `${seconds.toFixed(1)}s` : 'N/A';
  };

  const getStatusBadge = (status) => {
    const badges = {
      'pending': 'status-pending',
      'generating': 'status-generating', 
      'completed': 'status-completed',
      'failed': 'status-failed'
    };
    
    return badges[status] || 'status-unknown';
  };

  if (loading) {
    return (
      <div className="llm-log-viewer">
        <div className="loading">
          <div className="loading-spinner"></div>
          <p>Loading LLM logs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="llm-log-viewer">
      {/* Header with Status and Stats */}
      <div className="llm-overview">
        <h3>🤖 LLM System Status</h3>
        
        <div className="status-cards">
          {llmStatus && (
            <div className="status-card">
              <h4>Model Status</h4>
              <p><strong>Loaded:</strong> {llmStatus.model_loaded ? '✅ Yes' : '❌ No'}</p>
              {llmStatus.model_path && (
                <p><strong>Model:</strong> {llmStatus.model_path.split('/').pop()}</p>
              )}
              <p><strong>Generating:</strong> {llmStatus.currently_generating ? '🔄 Yes' : '⏹️ No'}</p>
              {llmStatus.error && (
                <p className="error-text"><strong>Error:</strong> {llmStatus.error}</p>
              )}
            </div>
          )}
          
          {stats && (
            <div className="status-card">
              <h4>Generation Stats</h4>
              <p><strong>Total:</strong> {stats.total_generations}</p>
              <p><strong>Success Rate:</strong> {stats.success_rate}%</p>
              <p><strong>Parse Success:</strong> {stats.parse_success_rate}%</p>
              <p><strong>Failed:</strong> {stats.failed}</p>
            </div>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="log-filters">
        <h4>🔍 Filter Logs</h4>
        <div className="filter-controls">
          <select 
            value={filter.status} 
            onChange={(e) => setFilter({...filter, status: e.target.value})}
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="generating">Generating</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
          
          <select 
            value={filter.prompt_type}
            onChange={(e) => setFilter({...filter, prompt_type: e.target.value})}
          >
            <option value="">All Types</option>
            <option value="monster_generation">Monster Generation</option>
          </select>
          
          <select 
            value={filter.limit}
            onChange={(e) => setFilter({...filter, limit: parseInt(e.target.value)})}
          >
            <option value="10">10 logs</option>
            <option value="20">20 logs</option>
            <option value="50">50 logs</option>
            <option value="100">100 logs</option>
          </select>
          
          <button onClick={loadAllData} className="refresh-button">
            🔄 Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <h4>❌ Error</h4>
          <p>{error}</p>
        </div>
      )}

      {/* Logs Table */}
      <div className="logs-section">
        <h4>📋 Recent LLM Logs ({logs.length})</h4>
        
        {logs.length === 0 ? (
          <p>No logs found. Try generating a monster to see logs appear here!</p>
        ) : (
          <div className="logs-table">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Time</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Duration</th>
                  <th>Tokens</th>
                  <th>Parse</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {logs.map(log => (
                  <tr key={log.id} className={getStatusBadge(log.status)}>
                    <td>{log.id}</td>
                    <td>{formatDate(log.created_at)}</td>
                    <td>{log.prompt_name}</td>
                    <td>
                      <span className={`status-badge ${getStatusBadge(log.status)}`}>
                        {log.status}
                      </span>
                    </td>
                    <td>{formatDuration(log.duration_seconds)}</td>
                    <td>{log.response_tokens || 'N/A'}</td>
                    <td>{log.parse_success ? '✅' : '❌'}</td>
                    <td>
                      <button 
                        onClick={() => handleLogClick(log.id)}
                        className="view-button"
                      >
                        👁️ View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Selected Log Detail */}
      {selectedLog && (
        <div className="log-detail">
          <h4>🔍 Log Detail - ID: {selectedLog.id}</h4>
          
          <div className="detail-sections">
            <div className="detail-section">
              <h5>📝 Prompt</h5>
              <div className="code-block">
                <pre>{selectedLog.prompt_text}</pre>
              </div>
            </div>
            
            {selectedLog.response_text && (
              <div className="detail-section">
                <h5>🤖 Response</h5>
                <div className="code-block">
                  <pre>{selectedLog.response_text}</pre>
                </div>
              </div>
            )}
            
            {selectedLog.parsed_data && (
              <div className="detail-section">
                <h5>✅ Parsed Data</h5>
                <div className="code-block">
                  <pre>{JSON.stringify(selectedLog.parsed_data, null, 2)}</pre>
                </div>
              </div>
            )}
            
            {selectedLog.parse_error && (
              <div className="detail-section error">
                <h5>❌ Parse Error</h5>
                <div className="error-block">
                  <pre>{selectedLog.parse_error}</pre>
                </div>
              </div>
            )}
            
            {selectedLog.error_message && (
              <div className="detail-section error">
                <h5>❌ Generation Error</h5>
                <div className="error-block">
                  <pre>{selectedLog.error_message}</pre>
                </div>
              </div>
            )}
          </div>
          
          <button 
            onClick={() => setSelectedLog(null)}
            className="close-button"
          >
            ✖️ Close Detail
          </button>
        </div>
      )}
    </div>
  );
}

export default LLMLogViewer;