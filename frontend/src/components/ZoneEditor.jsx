import React, { useState, useEffect, useRef } from 'react';
import { X, Save, RotateCcw, Plus, Trash2, CheckCircle2, Shield, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export default function ZoneEditor({ isOpen, onClose, onZoneSaved }) {
  const [points, setPoints] = useState([]);
  const [zoneName, setZoneName] = useState('Restricted Zone');
  const [zoneColor, setZoneColor] = useState('#EF4444');
  const [isActive, setIsActive] = useState(true);
  const [snapshotUrl, setSnapshotUrl] = useState('');
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [draggingIdx, setDraggingIdx] = useState(null);

  const canvasRef = useRef(null);
  const containerRef = useRef(null);

  // Load current zone config and fresh snapshot on open
  useEffect(() => {
    if (isOpen) {
      setSnapshotUrl(api.getSnapshotUrl(false));
      api.getZone()
        .then(data => {
          setZoneName(data.name || 'Restricted Zone');
          setZoneColor(data.color || '#EF4444');
          setIsActive(data.active ?? true);
          setPoints(data.points || []);
        })
        .catch(err => console.error('Failed to load zone:', err));
    }
  }, [isOpen]);

  // Redraw canvas whenever points or size changes
  useEffect(() => {
    if (!isOpen || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    if (points.length === 0) return;

    // Convert normalized (0-1) points to canvas pixels
    const pixelPts = points.map(p => ({
      x: p[0] * width,
      y: p[1] * height
    }));

    // Draw polygon fill
    if (pixelPts.length >= 3) {
      ctx.beginPath();
      ctx.moveTo(pixelPts[0].x, pixelPts[0].y);
      for (let i = 1; i < pixelPts.length; i++) {
        ctx.lineTo(pixelPts[i].x, pixelPts[i].y);
      }
      ctx.closePath();
      ctx.fillStyle = `${zoneColor}40`; // 25% alpha
      ctx.fill();

      // Polygon perimeter
      ctx.strokeStyle = zoneColor;
      ctx.lineWidth = 3;
      ctx.stroke();
    } else if (pixelPts.length === 2) {
      ctx.beginPath();
      ctx.moveTo(pixelPts[0].x, pixelPts[0].y);
      ctx.lineTo(pixelPts[1].x, pixelPts[1].y);
      ctx.strokeStyle = zoneColor;
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    // Draw vertices and index labels
    pixelPts.forEach((pt, i) => {
      // Glow circle
      ctx.beginPath();
      ctx.arc(pt.x, pt.y, 8, 0, Math.PI * 2);
      ctx.fillStyle = i === draggingIdx ? '#38bdf8' : '#ffffff';
      ctx.fill();
      ctx.strokeStyle = zoneColor;
      ctx.lineWidth = 3;
      ctx.stroke();

      // Text label
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 12px "Outfit", sans-serif';
      ctx.fillText(`P${i + 1}`, pt.x + 12, pt.y - 8);
    });
  }, [points, zoneColor, isOpen, draggingIdx]);

  if (!isOpen) return null;

  const handleCanvasClick = (e) => {
    if (draggingIdx !== null) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;

    // Check if clicked near existing point to avoid duplicates
    const hitIdx = points.findIndex(p => {
      const dx = (p[0] - x) * rect.width;
      const dy = (p[1] - y) * rect.height;
      return Math.sqrt(dx * dx + dy * dy) < 15;
    });

    if (hitIdx === -1) {
      setPoints([...points, [Number(x.toFixed(4)), Number(y.toFixed(4))]]);
    }
  };

  const handleMouseDown = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;

    const hitIdx = points.findIndex(p => {
      const dx = (p[0] - x) * rect.width;
      const dy = (p[1] - y) * rect.height;
      return Math.sqrt(dx * dx + dy * dy) < 18;
    });

    if (hitIdx !== -1) {
      setDraggingIdx(hitIdx);
    }
  };

  const handleMouseMove = (e) => {
    if (draggingIdx === null) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const y = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));

    const updated = [...points];
    updated[draggingIdx] = [Number(x.toFixed(4)), Number(y.toFixed(4))];
    setPoints(updated);
  };

  const handleMouseUp = () => {
    setDraggingIdx(null);
  };

  const handleReset = () => {
    setPoints([]);
  };

  const handlePreset = (presetType) => {
    if (presetType === 'center') {
      setPoints([[0.25, 0.25], [0.75, 0.25], [0.8, 0.85], [0.2, 0.85]]);
    } else if (presetType === 'bottom') {
      setPoints([[0.1, 0.45], [0.9, 0.45], [0.95, 0.95], [0.05, 0.95]]);
    } else if (presetType === 'left') {
      setPoints([[0.05, 0.15], [0.5, 0.15], [0.55, 0.9], [0.05, 0.9]]);
    }
  };

  const handleSave = async () => {
    if (points.length < 3) {
      alert('A restricted zone polygon requires at least 3 points.');
      return;
    }

    setSaving(true);
    try {
      await api.updateZone({
        name: zoneName,
        points: points,
        is_normalized: true,
        color: zoneColor,
        active: isActive
      });
      setSaveSuccess(true);
      if (onZoneSaved) onZoneSaved();
      setTimeout(() => {
        setSaveSuccess(false);
        onClose();
      }, 800);
    } catch (e) {
      console.error('Failed to save zone:', e);
      alert('Failed to save zone configuration.');
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
          maxWidth: '960px',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: '#0b0f19',
          border: '1px solid rgba(6, 182, 212, 0.4)',
          boxShadow: '0 20px 50px rgba(0, 0, 0, 0.8)',
          overflow: 'hidden'
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div style={{
          padding: '16px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'rgba(15, 23, 42, 0.8)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Shield size={20} color="var(--accent-cyan)" />
            <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#fff' }}>
              Interactive Zone Editor
            </h2>
          </div>
          <button
            onClick={onClose}
            className="btn-secondary"
            style={{ padding: '6px 8px', borderRadius: '8px' }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '20px 24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {/* Instructions banner */}
          <div style={{
            background: 'rgba(6, 182, 212, 0.1)',
            border: '1px solid rgba(6, 182, 212, 0.3)',
            borderRadius: '10px',
            padding: '10px 16px',
            fontSize: '13px',
            color: '#a5f3fc',
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            <AlertCircle size={18} color="#06b6d4" />
            <span>
              <strong>Click</strong> on the camera feed to place polygon vertices. <strong>Drag</strong> vertices to reposition. 3+ vertices form the restricted zone.
            </span>
          </div>

          {/* Canvas area with snapshot image background */}
          <div
            ref={containerRef}
            style={{
              position: 'relative',
              width: '100%',
              aspectRatio: '16/9',
              borderRadius: '12px',
              overflow: 'hidden',
              border: '2px solid rgba(255, 255, 255, 0.1)',
              backgroundColor: '#020408'
            }}
          >
            {snapshotUrl && (
              <img
                src={snapshotUrl}
                alt="Camera reference"
                style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
              />
            )}
            <canvas
              ref={canvasRef}
              width={960}
              height={540}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                cursor: draggingIdx !== null ? 'grabbing' : 'crosshair'
              }}
              onClick={handleCanvasClick}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
            />
          </div>

          {/* Zone Settings & Presets Row */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '16px',
            background: 'rgba(15, 23, 42, 0.5)',
            padding: '16px',
            borderRadius: '12px',
            border: '1px solid var(--border-subtle)'
          }}>
            {/* Zone Name */}
            <div>
              <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: '600' }}>
                Zone Label Name
              </label>
              <input
                type="text"
                value={zoneName}
                onChange={e => setZoneName(e.target.value)}
                style={{
                  width: '100%',
                  background: 'rgba(10, 14, 23, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '8px 12px',
                  color: '#fff',
                  fontSize: '13px'
                }}
              />
            </div>

            {/* Quick Presets */}
            <div>
              <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: '600' }}>
                Quick Presets
              </label>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                <button onClick={() => handlePreset('center')} className="btn-secondary" style={{ padding: '6px 10px', fontSize: '12px' }}>
                  Center Box
                </button>
                <button onClick={() => handlePreset('bottom')} className="btn-secondary" style={{ padding: '6px 10px', fontSize: '12px' }}>
                  Lower Half
                </button>
                <button onClick={() => handlePreset('left')} className="btn-secondary" style={{ padding: '6px 10px', fontSize: '12px' }}>
                  Left Wing
                </button>
              </div>
            </div>

            {/* Vertices Counter & Reset */}
            <div>
              <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: '600' }}>
                Vertices: {points.length}
              </label>
              <button
                onClick={handleReset}
                className="btn-secondary"
                style={{ padding: '6px 12px', fontSize: '12px', color: '#f87171' }}
              >
                <RotateCcw size={14} />
                <span>Clear All Points</span>
              </button>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div style={{
          padding: '16px 24px',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
          gap: '12px',
          background: 'rgba(15, 23, 42, 0.8)'
        }}>
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving || points.length < 3}
            className="btn-primary"
            style={{ minWidth: '130px' }}
          >
            {saveSuccess ? (
              <>
                <CheckCircle2 size={16} color="#fff" />
                <span>Zone Saved!</span>
              </>
            ) : (
              <>
                <Save size={16} />
                <span>{saving ? 'Saving...' : 'Apply Zone'}</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
