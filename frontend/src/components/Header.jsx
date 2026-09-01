import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, Bell, BellOff, Settings, Sliders, Volume2, VolumeX, Sparkles, RefreshCw } from 'lucide-react';

export default function Header({
  isAlerting,
  soundEnabled,
  onToggleSound,
  onOpenSettings,
  onOpenZoneEditor,
  onTriggerTestAlert,
  isTestingAlert,
  wsStatus
}) {
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString('en-US', { hour12: false }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="glass-panel" style={{
      margin: '16px 20px',
      padding: '14px 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '16px',
      borderLeft: isAlerting ? '4px solid var(--accent-red)' : '4px solid var(--accent-cyan)'
    }}>
      {/* Left: Brand / System Identity */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '12px',
          background: isAlerting ? 'linear-gradient(135deg, #ef4444, #991b1b)' : 'linear-gradient(135deg, #06b6d4, #0284c7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: isAlerting ? '0 0 20px var(--accent-red-glow)' : '0 0 16px var(--accent-cyan-glow)',
          transition: 'all 0.3s ease'
        }}>
          {isAlerting ? (
            <ShieldAlert size={24} color="#fff" />
          ) : (
            <Shield size={24} color="#fff" />
          )}
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 style={{ fontSize: '20px', fontWeight: '800', letterSpacing: '-0.02em', color: '#fff' }}>
              AI GUARD
            </h1>
            <span className="badge" style={{
              background: isAlerting ? 'rgba(239, 68, 68, 0.2)' : 'rgba(6, 182, 212, 0.15)',
              color: isAlerting ? '#f87171' : '#38bdf8',
              border: `1px solid ${isAlerting ? 'rgba(239, 68, 68, 0.4)' : 'rgba(6, 182, 212, 0.3)'}`
            }}>
              <span style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                backgroundColor: isAlerting ? '#ef4444' : '#06b6d4',
                display: 'inline-block'
              }} className={isAlerting ? "animate-live-dot" : ""} />
              {isAlerting ? 'BREACH DETECTED' : 'SYSTEM ARMED'}
            </span>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Intelligent Vision Surveillance &bull; YOLOv8 &bull; ByteTrack
          </p>
        </div>
      </div>

      {/* Center: Live Clock & System Connection */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 14px',
          background: 'rgba(15, 23, 42, 0.6)',
          borderRadius: '20px',
          border: '1px solid var(--border-subtle)'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: wsStatus === 'connected' ? '#10b981' : '#f59e0b'
          }} />
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            {wsStatus === 'connected' ? 'LIVE TELEMETRY' : 'RECONNECTING...'}
          </span>
          <span style={{ color: 'var(--border-subtle)' }}>|</span>
          <span className="mono" style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)' }}>
            {timeStr}
          </span>
        </div>
      </div>

      {/* Right: Quick Action Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        {/* Sound Alarm Toggle */}
        <button
          onClick={onToggleSound}
          className="btn-secondary"
          title={soundEnabled ? "Mute audio alarm" : "Unmute audio alarm"}
          style={{ padding: '8px 12px' }}
        >
          {soundEnabled ? (
            <>
              <Volume2 size={16} color="var(--accent-emerald)" />
              <span style={{ fontSize: '13px' }}>Audio On</span>
            </>
          ) : (
            <>
              <VolumeX size={16} color="var(--text-muted)" />
              <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Audio Muted</span>
            </>
          )}
        </button>

        {/* Test Alert Button */}
        <button
          onClick={onTriggerTestAlert}
          disabled={isTestingAlert}
          className="btn-secondary"
          title="Simulate intrusion to test pipeline"
          style={{ padding: '8px 12px' }}
        >
          <Sparkles size={16} color="var(--accent-amber)" />
          <span style={{ fontSize: '13px' }}>
            {isTestingAlert ? 'Testing...' : 'Test Alert'}
          </span>
        </button>

        {/* Zone Editor Toggle Button */}
        <button
          onClick={onOpenZoneEditor}
          className="btn-primary"
          style={{ padding: '8px 14px' }}
        >
          <Sliders size={16} />
          <span style={{ fontSize: '13px' }}>Edit Zone</span>
        </button>

        {/* Settings Modal Button */}
        <button
          onClick={onOpenSettings}
          className="btn-secondary"
          style={{ padding: '8px 12px' }}
          title="System Settings"
        >
          <Settings size={16} />
        </button>
      </div>
    </header>
  );
}
