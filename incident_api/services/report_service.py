"""
Servicio para la generación de informes de incidentes.
"""
from incident_api.models import Incident

def generate_incident_report_html(incident: Incident) -> str:
    """
    Genera un informe de incidente en formato HTML a partir de los datos del incidente.

    Args:
        incident: El objeto del incidente con todos sus datos relacionados.

    Returns:
        Un string con el contenido completo del informe en HTML.
    """

    # --- Helper functions para renderizar secciones ---
    def render_styles():
        return """
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; color: #212529; }
                .container { max-width: 800px; margin: 40px auto; padding: 30px; background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
                h1, h2, h3 { color: #0f766e; border-bottom: 2px solid #0f766e; padding-bottom: 10px; margin-top: 30px; }
                h1 { font-size: 2.5em; text-align: center; border: none; margin-bottom: 20px; }
                h2 { font-size: 1.8em; }
                h3 { font-size: 1.4em; border-bottom: 1px solid #ccc; color: #333; }
                .header { text-align: center; margin-bottom: 40px; }
                .ticket-id { display: inline-block; background-color: #f0fdfa; color: #0f766e; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 1.2em; border: 1px solid #ccfbf1; }
                .section { margin-bottom: 30px; }
                .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
                .grid-item { background-color: #f8f9fa; padding: 15px; border-radius: 5px; border: 1px solid #e9ecef; }
                .grid-item strong { display: block; margin-bottom: 5px; color: #495057; }
                .pre-wrap { white-space: pre-wrap; word-wrap: break-word; background-color: #f8f9fa; padding: 15px; border-radius: 5px; border: 1px solid #e9ecef; font-family: "Courier New", Courier, monospace; }
                ul { list-style-type: none; padding-left: 0; }
                li { background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 8px; border-left: 4px solid #14b8a6; }
                .log-item { border-left: 3px solid #6c757d; margin-bottom: 15px; padding-left: 15px; }
                .log-meta { font-size: 0.9em; color: #6c757d; }
                .footer { text-align: center; margin-top: 40px; font-size: 0.8em; color: #6c757d; }
            </style>
        """

    def render_header(incident: Incident):
        return f"""
            <div class="header">
                <h1>Informe de Incidente de Seguridad</h1>
                <div class="ticket-id">Ticket: {incident.ticket_id}</div>
            </div>
        """

    def render_summary(incident: Incident):
        return f"""
            <div class="section">
                <h2>1. Resumen del Incidente</h2>
                <p>{incident.summary}</p>
                <h3>Descripción Detallada</h3>
                <p class="pre-wrap">{incident.description}</p>
            </div>
        """

    def render_details(incident: Incident):
        status_class = incident.status.lower()
        severity_class = incident.severity.lower().replace('(', '').replace(')', '').replace(' ', '-')
        return f"""
            <div class="section">
                <h2>2. Detalles y Clasificación</h2>
                <div class="grid">
                    <div class="grid-item"><strong>Estado:</strong> <span class="status-{status_class}">{incident.status}</span></div>
                    <div class="grid-item"><strong>Severidad:</strong> <span class="severity-{severity_class}">{incident.severity}</span></div>
                    <div class="grid-item"><strong>Categoría:</strong> {incident.incident_category.name if incident.incident_category else 'N/A'}</div>
                    <div class="grid-item"><strong>Tipo de Incidente:</strong> {incident.incident_type.name if incident.incident_type else 'N/A'}</div>
                    <div class="grid-item"><strong>Responsable:</strong> {incident.assignee.full_name if incident.assignee else (incident.assignee_group.name + ' (Grupo)' if incident.assignee_group else 'Sin asignar')}</div>
                    <div class="grid-item"><strong>Vector de Ataque:</strong> {incident.attack_vector.name if incident.attack_vector else 'N/A'}</div>
                </div>
            </div>
        """

    def render_analysis(incident: Incident):
        return f"""
            <div class="section">
                <h2>3. Análisis y Respuesta</h2>
                <h3>Análisis de Causa Raíz</h3>
                <div class="pre-wrap">{incident.root_cause_analysis or 'No documentado.'}</div>
                <h3>Acciones de Contención</h3>
                <div class="pre-wrap">{incident.containment_actions or 'No documentado.'}</div>
                <h3>Acciones de Recuperación</h3>
                <div class="pre-wrap">{incident.recovery_actions or 'No documentado.'}</div>
                <h3>Acciones Correctivas</h3>
                <div class="pre-wrap">{incident.corrective_actions or 'No documentado.'}</div>
                <h3>Lecciones Aprendidas</h3>
                <div class="pre-wrap">{incident.lessons_learned or 'No documentado.'}</div>
            </div>
        """

    def render_evidence(incident: Incident):
        if not incident.evidence_files:
            return ""
        items = "".join([f"<li>{file.file_name}</li>" for file in incident.evidence_files])
        return f"""
            <div class="section">
                <h2>4. Evidencia Adjunta</h2>
                <ul>{items}</ul>
            </div>
        """

    def render_logs(incident: Incident):
        if not incident.logs:
            return ""
        log_items = "".join([
            f"""<div class="log-item">
                <p><strong>{log.action}:</strong> {log.comments or 'Sin comentarios adicionales.'}</p>
                <div class="log-meta">Por: {log.user.full_name if log.user else 'Sistema'} - {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>""" for log in sorted(incident.logs, key=lambda x: x.timestamp)
        ])
        return f"""
            <div class="section">
                <h2>5. Bitácora del Incidente</h2>
                {log_items}
            </div>
        """

    # --- Construcción del Documento HTML ---
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Informe de Incidente: {incident.ticket_id}</title>
        {render_styles()}
    </head>
    <body>
        <div class="container">
            {render_header(incident)}
            {render_summary(incident)}
            {render_details(incident)}
            {render_analysis(incident)}
            {render_evidence(incident)}
            {render_logs(incident)}
            <div class="footer">
                <p>Informe generado el {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html
