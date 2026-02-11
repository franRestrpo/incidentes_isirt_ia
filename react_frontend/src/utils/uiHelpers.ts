/**
 * Funciones de Ayuda de UI
 *
 * Este módulo de utilidades contiene funciones reutilizables para lógica de presentación de UI.
 * Estas funciones manejan transformaciones comunes de UI y decisiones de estilo,
 * promoviendo consistencia en la aplicación y evitando duplicación de código.
 *
 * Utilidades actuales:
 * - Estilo de badges de estado para estados de incidentes
 * - Estilo de badges de severidad para prioridades de incidentes
 *
 * Estas funciones son puras y pueden ser fácilmente testeadas. Encapsulan
 * lógica de negocio para representación visual sin acoplarse a componentes específicos.
 */

/**
 * Devuelve la clase CSS apropiada para badges de estado basado en el estado del incidente.
 * @param status La cadena de estado del incidente
 * @returns Nombre de clase CSS para el badge de estado
 */
export const getStatusBadgeClass = (status: string): string => {
  const statusLower = status.toLowerCase();
  if (statusLower.includes('nuevo') || statusLower.includes('open')) return 'status-nuevo';
  if (statusLower.includes('analisis') || statusLower.includes('in-progress') || statusLower.includes('investigando')) return 'status-analisis';
  if (statusLower.includes('contenido') || statusLower.includes('on-hold')) return 'status-contenido';
  if (statusLower.includes('erradicado')) return 'status-erradicado';
  if (statusLower.includes('recuperando')) return 'status-recuperando';
  if (statusLower.includes('resuelto')) return 'status-resuelto';
  if (statusLower.includes('cerrado') || statusLower.includes('closed')) return 'status-cerrado';
  return 'status-nuevo'; // default
};

/**
 * Devuelve la clase CSS apropiada para badges de severidad basado en la severidad del incidente.
 * @param severity La cadena de severidad del incidente
 * @returns Nombre de clase CSS para el badge de severidad
 */
export const getSeverityBadgeClass = (severity: string): string => {
  const severityLower = severity.toLowerCase();
  if (severityLower.includes('bajo')) return 'severity-bajo';
  if (severityLower.includes('medio')) return 'severity-medio';
  if (severityLower.includes('alto')) return 'severity-alto';
  if (severityLower.includes('critico')) return 'severity-critico';
  return 'severity-medio'; // default
};