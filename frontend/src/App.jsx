import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import StatusBar from './components/StatusBar';
import Dashboard from './components/Dashboard';
import ZoneEditor from './components/ZoneEditor';
import SettingsModal from './components/SettingsModal';
import { api, connectAlertWebSocket } from './services/api';

export default function App() {
  const [status, setStatus] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [wsStatus, setWsStatus] = useState('connecting');
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [isZoneEditorOpen, setIsZoneEditorOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isTestingAlert, setIsTestingAlert] = useState(false);

  const audioCtxRef = useRef(null);

  // Synthesize tactical alarm tone via Web Audio API
  const playAlertSound = () => {
    if (!soundEnabled) return;
    try {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)();
      }
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') {
        ctx.resume();
      }

      // 2-tone tactical siren (880Hz -> 660Hz)
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(880, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.35);

      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.35);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 0.35);
    } catch (e) {
      console.warn('Audio tone could not play:', e);
    }
  };

  // Initial data loading
  useEffect(() => {
    // 1. Fetch initial status
    api.getStatus()
      .then(setStatus)
      .catch(err => console.error('Initial status error:', err));

    // 2. Fetch recent alerts
    api.getAlerts(50)
      .then(setAlerts)
      .catch(err => console.error('Initial alerts error:', err));

    // 3. Connect WebSocket for live telemetry & alerts
    const ws = connectAlertWebSocket(
      (payload) => {
        if (payload.type === 'SYSTEM_STATUS') {
          setStatus(payload.data);
        } else if (payload.type === 'INTRUSION_ALERT') {
          const newAlert = payload.data;
          setAlerts(prev => [newAlert, ...prev.filter(a => a.id !== newAlert.id)]);
          playAlertSound();
        }
      },
      (newStatus) => setWsStatus(newStatus)
    );

    return () => ws.close();
  }, [soundEnabled]);

  const handleClearAlerts = async () => {
    try {
      await api.clearAlerts();
      setAlerts([]);
    } catch (err) {
      console.error('Failed to clear alerts:', err);
    }
  };

  const handleTriggerTestAlert = async () => {
    setIsTestingAlert(true);
    try {
      const res = await api.triggerTestAlert();
      if (res.status === 'success' && res.alert) {
        setAlerts(prev => [res.alert, ...prev]);
        playAlertSound();
      } else if (res.status === 'cooldown') {
        alert(res.message);
      }
    } catch (err) {
      console.error('Test alert failed:', err);
    } finally {
      setIsTestingAlert(false);
    }
  };

  const isAlerting = Boolean(status?.zone_intruders_count && status.zone_intruders_count > 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Top Header */}
      <Header
        isAlerting={isAlerting}
        soundEnabled={soundEnabled}
        onToggleSound={() => setSoundEnabled(prev => !prev)}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenZoneEditor={() => setIsZoneEditorOpen(true)}
        onTriggerTestAlert={handleTriggerTestAlert}
        isTestingAlert={isTestingAlert}
        wsStatus={wsStatus}
      />

      {/* Metrics Status Bar */}
      <StatusBar
        status={status}
        isAlerting={isAlerting}
      />

      {/* Live Stream & Alert Feed Grid */}
      <Dashboard
        isAlerting={isAlerting}
        intrudersCount={status?.zone_intruders_count || 0}
        alerts={alerts}
        onClearAlerts={handleClearAlerts}
      />

      {/* Interactive Zone Editor Modal */}
      <ZoneEditor
        isOpen={isZoneEditorOpen}
        onClose={() => setIsZoneEditorOpen(false)}
        onZoneSaved={() => {
          api.getStatus().then(setStatus);
        }}
      />

      {/* Configuration Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSettingsUpdated={() => {
          api.getStatus().then(setStatus);
        }}
      />
    </div>
  );
}
