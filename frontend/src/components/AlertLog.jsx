import React, { useState } from 'react';
import { AlertTriangle, Clock, Users, Trash2, ExternalLink, X, Download, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';

export default function AlertLog({ alerts, onClearAlerts }) {
  const [selectedAlert, setSelectedAlert] = useState(null);

  return (
    <div className="glass-panel" style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      minHeight: '480px',
      overflow: 'hidden'
    }}>
      {/* Panel Header */}
      <div style={{
        padding: '14px 18px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'rgba(10, 14, 23, 0.8)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={18} color="var(--accent-red)" />
          <h2 style={{ fontSize: '15px', fontWeight: '700', color: '#fff' }}>
            Intrusion Event Log
          </h2>
          <span className="badge badge-cyan" style={{ fontSize: '11px', padding: '2px 8px' }}>
            {alerts.length}
          </span>
        </div>

        {alerts.length > 0 && (
          <button
            onClick={onClearAlerts}
            className="btn-secondary"
            title="Clear all alerts"
            style={{ padding: '6px 10px', fontSize: '12px', color: '#f87171' }}
          >
            <Trash2 size={13} />
            <span>Clear</span>
          </button>
        )}
      </div>

      {/* Alerts Scrollable List */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '14px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px'
      }}>
        {alerts.length === 0 ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            minHeight: '280px',
            color: 'var(--text-muted)',
            textAlign: 'center',
            padding: '20px'
          }}>
            <ShieldCheck size={44} color="var(--accent-emerald)" style={{ marginBottom: '12px', opacity: 0.8 }} />
            <div style={{ fontSize: '15px', fontWeight: '600', color: 'var(--text-secondary)' }}>
              No Intrusion Events Recorded
            </div>
            <div style={{ fontSize: '12px', marginTop: '6px', maxWidth: '240px' }}>
              The monitored security zone is clear. Any detected person crossing into the zone will appear here with a snapshot.
            </div>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className="glass-panel"
              style={{
                padding: '12px',
                backgroundColor: 'rgba(15, 23, 42, 0.75)',
                borderLeft: '3px solid var(--accent-red)',
                display: 'flex',
                gap: '12px',
                cursor: 'pointer',
                transition: 'transform 0.2s ease, border-color 0.2s ease'
              }}
              onClick={() => setSelectedAlert(alert)}
            >
              {/* Thumbnail Image */}
              <div style={{
                width: '74px',
                height: '56px',
                borderRadius: '6px',
                overflow: 'hidden',
                backgroundColor: '#000',
                flexShrink: 0,
                border: '1px solid var(--border-subtle)'
              }}>
                <img
                  src={alert.screenshot_url || `/api/alerts/${alert.id}/screenshot`}
                  alt={`Alert ${alert.id}`}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              </div>

              {/* Alert Details */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontSize: '13px', fontWeight: '700', color: '#fca5a5' }}>
                    🚨 {alert.zone_name}
                  </span>
                  <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    {alert.timestamp?.split(' ')[1] || alert.timestamp}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Users size={13} color="var(--accent-cyan)" />
                    <span>{alert.intruder_count} Person{alert.intruder_count > 1 ? 's' : ''}</span>
                  </div>
                  {alert.tracker_ids?.length > 0 && (
                    <span className="mono" style={{ color: 'var(--text-muted)' }}>
                      IDs: #{alert.tracker_ids.join(', #')}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Full-Resolution Screenshot Modal */}
      {selectedAlert && (
        <div className="modal-overlay" onClick={() => setSelectedAlert(null)}>
          <div
            className="glass-panel"
            style={{
              width: '92%',
              maxWidth: '840px',
              backgroundColor: '#0a0d14',
              border: '1px solid var(--accent-red)',
              overflow: 'hidden'
            }}
            onClick={e => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div style={{
              padding: '14px 20px',
              borderBottom: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#f87171' }}>
                  🚨 Intrusion Evidence — {selectedAlert.id}
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  {selectedAlert.timestamp} &bull; {selectedAlert.zone_name}
                </p>
              </div>
              <button
                onClick={() => setSelectedAlert(null)}
                className="btn-secondary"
                style={{ padding: '6px 8px' }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Modal Image */}
            <div style={{ padding: '16px', backgroundColor: '#020408', display: 'flex', justifyContent: 'center' }}>
              <img
                src={selectedAlert.screenshot_url || `/api/alerts/${selectedAlert.id}/screenshot`}
                alt="Intrusion snapshot"
                style={{
                  width: '100%',
                  maxHeight: '65vh',
                  objectFit: 'contain',
                  borderRadius: '8px',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}
              />
            </div>

            {/* Modal Footer */}
            <div style={{
              padding: '12px 20px',
              borderTop: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Tracked Intruder IDs: <span className="mono">#{selectedAlert.tracker_ids?.join(', #') || 'N/A'}</span>
              </div>
              <a
                href={selectedAlert.screenshot_url || `/api/alerts/${selectedAlert.id}/screenshot`}
                download={`intrusion_${selectedAlert.id}.jpg`}
                className="btn-primary"
                style={{ padding: '6px 14px', fontSize: '12px', textDecoration: 'none' }}
              >
                <Download size={14} />
                <span>Download Image</span>
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
