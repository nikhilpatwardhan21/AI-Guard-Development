const API_BASE = '/api';

export const api = {
  // System Status
  async getStatus() {
    const res = await fetch(`${API_BASE}/status`);
    if (!res.ok) throw new Error('Failed to fetch status');
    return res.json();
  },

  // Alerts
  async getAlerts(limit = 50) {
    const res = await fetch(`${API_BASE}/alerts?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch alerts');
    return res.json();
  },

  async clearAlerts() {
    const res = await fetch(`${API_BASE}/alerts`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to clear alerts');
    return res.json();
  },

  // Zone configuration
  async getZone() {
    const res = await fetch(`${API_BASE}/zone`);
    if (!res.ok) throw new Error('Failed to fetch zone config');
    return res.json();
  },

  async updateZone(zoneConfig) {
    const res = await fetch(`${API_BASE}/zone`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(zoneConfig),
    });
    if (!res.ok) throw new Error('Failed to update zone');
    return res.json();
  },

  // Settings
  async updateSettings(settings) {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings),
    });
    if (!res.ok) throw new Error('Failed to update settings');
    return res.json();
  },

  // Trigger test alert
  async triggerTestAlert() {
    const res = await fetch(`${API_BASE}/test-alert`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to trigger test alert');
    return res.json();
  },

  // Stream URL helper
  getStreamUrl() {
    return `${API_BASE}/stream`;
  },

  // Snapshot URL helper
  getSnapshotUrl(annotated = true) {
    return `${API_BASE}/snapshot?annotated=${annotated}&t=${Date.now()}`;
  }
};

/**
 * WebSocket manager with automatic reconnection
 */
export function connectAlertWebSocket(onMessage, onStatusChange) {
  let ws = null;
  let reconnectTimer = null;
  let isClosedManually = false;

  function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/alerts`;

    try {
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        if (onStatusChange) onStatusChange('connected');
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (onMessage) onMessage(payload);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      ws.onclose = () => {
        if (onStatusChange) onStatusChange('disconnected');
        if (!isClosedManually) {
          reconnectTimer = setTimeout(connect, 3000);
        }
      };

      ws.onerror = () => {
        if (onStatusChange) onStatusChange('error');
        ws.close();
      };
    } catch (e) {
      console.error('WebSocket connection error:', e);
      if (!isClosedManually) {
        reconnectTimer = setTimeout(connect, 3000);
      }
    }
  }

  connect();

  return {
    close() {
      isClosedManually = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws) ws.close();
    },
    send(data) {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(typeof data === 'string' ? data : JSON.stringify(data));
      }
    }
  };
}
