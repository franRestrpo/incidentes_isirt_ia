// src/components/audit/MetricsCards.tsx
import { Card, Metric, Text, Grid, Col } from '@tremor/react';

// Assuming the metrics object structure from our backend schema
interface MetricsProps {
  metrics: {
    total_incidents_created: number;
    total_incidents_resolved: number;
    last_login: string | null;
    top_incident_types: string[];
  };
}

export default function MetricsCards({ metrics }: MetricsProps) {
  const formattedLastLogin = metrics.last_login
    ? new Date(metrics.last_login).toLocaleString()
    : 'Nunca';

  return (
    <Grid numItemsMd={2} numItemsLg={4} className="gap-6">
      <Col>
        <Card>
          <Text>Incidentes Creados</Text>
          <Metric>{metrics.total_incidents_created}</Metric>
        </Card>
      </Col>
      <Col>
        <Card>
          <Text>Incidentes Resueltos</Text>
          <Metric>{metrics.total_incidents_resolved}</Metric>
        </Card>
      </Col>
      <Col>
        <Card>
          <Text>Último Inicio de Sesión</Text>
          <Metric>{formattedLastLogin}</Metric>
        </Card>
      </Col>
      <Col>
        <Card>
          <Text>Principales Tipos de Incidentes</Text>
          <Text className="mt-2">{metrics.top_incident_types.join(', ') || 'N/A'}</Text>
        </Card>
      </Col>
    </Grid>
  );
}
