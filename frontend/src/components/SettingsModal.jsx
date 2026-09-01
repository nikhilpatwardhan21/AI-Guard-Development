import React, { useState } from 'react';
import { X, Save, Sliders, Mail, Video, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

export default function SettingsModal({ isOpen, onClose, onSettingsUpdated }) {
  const [confidence, setConfidence] = useState(45);
  const [cooldown, setCooldown] = useState(30);
  const [cameraSource, setCameraSource] = useState('0');
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [alertRecipient, setAlertRecipient] = useState('');
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.updateSettings({
        confidence_threshold: confidence / 100,
        alert_cooldown_seconds: parseInt(cooldown),
        camera_source: cameraSource,
        email_enabled: emailEnabled,
        alert_recipient: alertRecipient
      });
      setSavedSuccess(true);
      if (onSettingsUpdated) onSettingsUpdated();
      setTimeout(() => {
        setSavedSuccess(false);
        onClose();
      }, 700);
    } catch (err) {
      console.error('Failed to update settings:', err);
      alert('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="glass-panel"
        style={{
          width: '94%',
          maxWidth: '560px',
          backgroundColor: '#0c101a',
          border: '1px solid rgba(6, 182, 212, 0.4)',
          overflow: 'hidden'
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'rgba(15, 23, 42, 0.8)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Sliders size={20} color="var(--accent-cyan)" />
            <h2 style={{ fontSize: '17px', fontWeight: '700', color: '#fff' }}>
              System Configuration
            </h2>
          </div>
          <button onClick={onClose} className="btn-secondary" style={{ padding: '6px 8px' }}>
            <X size={18} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSave} style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {/* Section 1: Vision & Detection */}
          <div>
            <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--accent-cyan)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Video size={16} />
              <span>Vision & Detection</span>
            </div>

            {/* Confidence Slider */}
            <div style={{ marginBottom: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
                <label style={{ color: 'var(--text-secondary)' }}>YOLO Confidence Threshold</label>
                <span className="mono" style={{ color: 'var(--accent-cyan)', fontWeight: '600' }}>{confidence}%</span>
              </div>
              <input
                type="range"
                min="15"
                max="90"
                value={confidence}
                onChange={e => setConfidence(Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--accent-cyan)' }}
              />
            </div>

            {/* Alert Cooldown Slider */}
            <div style={{ marginBottom: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
                <label style={{ color: 'var(--text-secondary)' }}>Alert Cooldown Period</label>
                <span className="mono" style={{ color: 'var(--accent-amber)', fontWeight: '600' }}>{cooldown}s</span>
              </div>
              <input
                type="range"
                min="5"
                max="120"
                step="5"
                value={cooldown}
                onChange={e => setCooldown(Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--accent-amber)' }}
              />
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                Suppresses duplicate alerts for the same person within this duration.
              </span>
            </div>

            {/* Camera Source */}
            <div>
              <label style={{ display: 'block', fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                Camera Source
              </label>
              <input
                type="text"
                value={cameraSource}
                onChange={e => setCameraSource(e.target.value)}
                placeholder="0 (Webcam) or rtsp://... or path.mp4"
                style={{
                  width: '100%',
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '8px 12px',
                  color: '#fff',
                  fontSize: '13px'
                }}
              />
            </div>
          </div>

          <hr style={{ border: 'none', borderTop: '1px solid var(--border-subtle)' }} />

          {/* Section 2: Email Notifications */}
          <div>
            <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--accent-emerald)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Mail size={16} />
              <span>Email Notification Delivery</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Enable Email Alerts</span>
              <input
                type="checkbox"
                checked={emailEnabled}
                onChange={e => setEmailEnabled(e.target.checked)}
                style={{ width: '18px', height: '18px', accentColor: 'var(--accent-emerald)' }}
              />
            </div>

            {emailEnabled && (
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Alert Recipient Email
                </label>
                <input
                  type="email"
                  value={alertRecipient}
                  onChange={e => setAlertRecipient(e.target.value)}
                  placeholder="security-admin@example.com"
                  style={{
                    width: '100%',
                    background: 'rgba(15, 23, 42, 0.8)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    padding: '8px 12px',
                    color: '#fff',
                    fontSize: '13px'
                  }}
                />
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px', display: 'block' }}>
                  SMTP server credentials can be defined in <code>backend/.env</code>.
                </span>
              </div>
            )}
          </div>

          {/* Footer buttons */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={saving} className="btn-primary" style={{ minWidth: '120px' }}>
              {savedSuccess ? (
                <>
                  <CheckCircle2 size={16} color="#fff" />
                  <span>Applied</span>
                </>
              ) : (
                <>
                  <Save size={16} />
                  <span>{saving ? 'Saving...' : 'Save Settings'}</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
