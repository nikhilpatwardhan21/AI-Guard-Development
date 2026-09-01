import React from 'react';
import { Video, Cpu, Users, AlertTriangle, Mail, Activity } from 'lucide-react';

export default function StatusBar({ status, isAlerting }) {
  const fps = status?.current_fps || 0;
  const persons = status?.total_persons_detected || 0;
  const intruders = status?.zone_intruders_count || 0;
  const cameraActive = status?.camera_active ?? false;
  const zoneActive = status?.zone_active ?? true;
  const emailEnabled = status?.email_alerts_enabled ?? false;

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '16px',
      margin: '0 20px 20px 20px'
    }}>
      {/* 1. Camera Status Card */}
      <div className="glass-panel" style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: '500' }}>Camera Feed</span>
          <Video size={18} color={cameraActive ? 'var(--accent-emerald)' : 'var(--accent-amber)'} />
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
          <span style={{ fontSize: '20px', fontWeight: '700', color: cameraActive ? '#fff' : 'var(--accent-amber)' }}>
            {cameraActive ? 'Online' : 'Standby'}
          </span>
          <span className="badge badge-online" style={{ fontSize: '11px', padding: '2px 8px' }}>
            Live
          </span>
        </div>
        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
          Real-time MJPEG stream
        </div>
      </div>

      {/* 2. Inference FPS */}
      <div className="glass-panel" style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: '500' }}>Inference Speed</span>
          <Activity size={18} color="var(--accent-cyan)" />
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
          <span className="mono" style={{ fontSize: '24px', fontWeight: '800', color: fps > 18 ? 'var(--accent-emerald)' : fps > 10 ? 'var(--accent-amber)' : 'var(--accent-red)' }}>
            {fps.toFixed(1)}
          </span>
          <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>FPS</span>
        </div>
        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
          YOLOv8 + ByteTrack pipeline
        </div>
      </div>

      {/* 3. Persons in Field of View */}
      <div className="glass-panel" style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: '500' }}>People Tracked</span>
          <Users size={18} color="var(--accent-purple)" />
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
          <span className="mono" style={{ fontSize: '24px', fontWeight: '800', color: '#fff' }}>
            {persons}
          </span>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            {persons === 1 ? 'person detected' : 'people detected'}
          </span>
        </div>
        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
          Active IDs: {status?.active_tracker_ids?.length > 0 ? `#${status.active_tracker_ids.join(', #')}` : 'None'}
        </div>
      </div>

      {/* 4. Zone Status / Intruders */}
      <div className={`glass-panel ${intruders > 0 ? 'glass-panel-alert' : ''}`} style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ fontSize: '13px', color: intruders > 0 ? '#fca5a5' : 'var(--text-secondary)', fontWeight: '500' }}>
            Restricted Zone
          </span>
          <AlertTriangle size={18} color={intruders > 0 ? 'var(--accent-red)' : 'var(--accent-cyan)'} />
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
          <span className="mono" style={{ fontSize: '24px', fontWeight: '800', color: intruders > 0 ? 'var(--accent-red)' : 'var(--accent-emerald)' }}>
            {intruders}
          </span>
          <span className="badge" style={{
            background: intruders > 0 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.15)',
            color: intruders > 0 ? '#f87171' : '#34d399',
            border: `1px solid ${intruders > 0 ? 'rgba(239, 68, 68, 0.4)' : 'rgba(16, 185, 129, 0.3)'}`
          }}>
            {intruders > 0 ? 'INTRUDER DETECTED' : zoneActive ? 'ARMED & SECURE' : 'DISARMED'}
          </span>
        </div>
        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
          Feet anchor trigger active
        </div>
      </div>

      {/* 5. Email Notifications Status */}
      <div className="glass-panel" style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: '500' }}>Email Dispatch</span>
          <Mail size={18} color={emailEnabled ? 'var(--accent-emerald)' : 'var(--text-muted)'} />
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
          <span style={{ fontSize: '18px', fontWeight: '700', color: emailEnabled ? '#fff' : 'var(--text-muted)' }}>
            {emailEnabled ? 'Enabled' : 'Disabled'}
          </span>
        </div>
        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
          {emailEnabled ? 'Dispatching with screenshot' : 'Configure SMTP in settings'}
        </div>
      </div>
    </div>
  );
}
