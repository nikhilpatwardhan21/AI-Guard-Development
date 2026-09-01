import React, { useState, useRef } from 'react';
import { Maximize2, Camera, RefreshCw, AlertOctagon, ShieldCheck, Eye, EyeOff } from 'lucide-react';
import { api } from '../services/api';

export default function LiveStream({ isAlerting, intrudersCount }) {
  const [streamKey, setStreamKey] = useState(Date.now());
  const [isLoading, setIsLoading] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef(null);

  const handleRefresh = () => {
    setIsLoading(true);
    setStreamKey(Date.now());
    setTimeout(() => setIsLoading(false), 500);
  };

  const handleCaptureSnapshot = async () => {
    try {
      const url = api.getSnapshotUrl(true);
      const link = document.createElement('a');
      link.href = url;
      link.download = `guard_snapshot_${Date.now()}.jpg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (e) {
      console.error('Failed to download snapshot:', e);
    }
  };

  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().catch(err => console.error(err));
      setIsFullscreen(true);
    } else {
      document.exitFullscreen().catch(err => console.error(err));
      setIsFullscreen(false);
    }
  };

  return (
    <div
      ref={containerRef}
      className={`glass-panel ${isAlerting ? 'glass-panel-alert' : ''}`}
      style={{
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        minHeight: '480px',
        backgroundColor: '#05070d'
      }}
    >
      {/* Top Stream Header Bar */}
      <div style={{
        padding: '12px 18px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'rgba(10, 14, 23, 0.8)',
        zIndex: 10
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: isAlerting ? 'var(--accent-red)' : 'var(--accent-emerald)',
          }} className={isAlerting ? "animate-live-dot" : ""} />
          <span style={{ fontSize: '14px', fontWeight: '700', letterSpacing: '0.02em', color: '#fff' }}>
            SURVEILLANCE CAM 01 &bull; MAIN FEED
          </span>
          <span className="badge badge-live" style={{
            background: isAlerting ? 'rgba(239, 68, 68, 0.25)' : 'rgba(16, 185, 129, 0.15)',
            color: isAlerting ? '#f87171' : '#34d399',
            borderColor: isAlerting ? 'var(--accent-red)' : 'rgba(16, 185, 129, 0.3)'
          }}>
            {isAlerting ? `⚠️ INTRUSION (${intrudersCount})` : 'SECURE'}
          </span>
        </div>

        {/* Action icons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={handleCaptureSnapshot}
            className="btn-secondary"
            title="Download Instant Snapshot"
            style={{ padding: '6px 10px', fontSize: '12px' }}
          >
            <Camera size={14} />
            <span>Snapshot</span>
          </button>

          <button
            onClick={handleRefresh}
            className="btn-secondary"
            title="Reconnect Stream"
            style={{ padding: '6px 10px', fontSize: '12px' }}
          >
            <RefreshCw size={14} className={isLoading ? "animate-spin" : ""} />
          </button>

          <button
            onClick={toggleFullscreen}
            className="btn-secondary"
            title="Toggle Fullscreen"
            style={{ padding: '6px 10px', fontSize: '12px' }}
          >
            <Maximize2 size={14} />
          </button>
        </div>
      </div>

      {/* Main Stream Image / Canvas Container */}
      <div style={{
        position: 'relative',
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#020408',
        minHeight: '420px',
        overflow: 'hidden'
      }}>
        <img
          key={streamKey}
          src={`${api.getStreamUrl()}?t=${streamKey}`}
          alt="AI Guard Video Feed"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            display: 'block'
          }}
          onError={(e) => {
            console.warn('Stream reload needed:', e);
          }}
        />

        {/* Intrusion Warning Overlay Banner */}
        {isAlerting && (
          <div style={{
            position: 'absolute',
            bottom: '16px',
            left: '50%',
            transform: 'translateX(-50%)',
            background: 'rgba(220, 38, 38, 0.92)',
            backdropFilter: 'blur(8px)',
            color: '#fff',
            padding: '10px 24px',
            borderRadius: '12px',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            boxShadow: '0 8px 32px rgba(239, 68, 68, 0.6)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            zIndex: 20
          }} className="animate-slide-in">
            <AlertOctagon size={22} color="#fff" />
            <div style={{ fontSize: '14px', fontWeight: '700', letterSpacing: '0.02em' }}>
              RESTRICTED ZONE BREACHED — {intrudersCount} PERSON(S) DETECTED
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
