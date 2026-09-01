import React from 'react';
import LiveStream from './LiveStream';
import AlertLog from './AlertLog';

export default function Dashboard({
  isAlerting,
  intrudersCount,
  alerts,
  onClearAlerts
}) {
  return (
    <main style={{
      display: 'grid',
      gridTemplateColumns: 'minmax(0, 1.8fr) minmax(320px, 1.1fr)',
      gap: '20px',
      margin: '0 20px 20px 20px',
      flex: 1
    }}>
      {/* Primary Video Feed Stream */}
      <section style={{ display: 'flex', flexDirection: 'column' }}>
        <LiveStream
          isAlerting={isAlerting}
          intrudersCount={intrudersCount}
        />
      </section>

      {/* Real-Time Alert Log Panel */}
      <section style={{ display: 'flex', flexDirection: 'column' }}>
        <AlertLog
          alerts={alerts}
          onClearAlerts={onClearAlerts}
        />
      </section>
    </main>
  );
}
