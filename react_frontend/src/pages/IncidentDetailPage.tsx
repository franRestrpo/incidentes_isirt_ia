import React, { useRef, useEffect, useState } from 'react';
import { useIncident } from '../hooks/useIncident';
import IncidentBasicInfo from '../components/incident/IncidentBasicInfo';
import IncidentAIConversation from '../components/incident/IncidentAIConversation';
import IncidentAISummary from '../components/incident/IncidentAISummary';
import IncidentEvidence from '../components/incident/IncidentEvidence';
import IncidentTriageForm from '../components/incident/IncidentTriageForm';
import IncidentAnalysisSection from '../components/incident/IncidentAnalysisSection';
import RAGSuggestionDisplay from '../components/incident/RAGSuggestionDisplay';
import IncidentClosureSection from '../components/incident/IncidentClosureSection';
import IncidentLogTimeline from '../components/incident/IncidentLogTimeline';
import { Button, Text } from '@tremor/react';

const IncidentDetailPage: React.FC = () => {
  const triageSectionRef = useRef<HTMLDivElement>(null);
  const analysisSectionRef = useRef<HTMLDivElement>(null);
  const [scrollToSection, setScrollToSection] = useState<'triage' | 'analysis' | null>(null);

  const {
    incident,
    users,
    groups,
    categories,
    attackVectors,
    assetTypes,
    assets,
    incidentTypes,
    logs,
    loading,
    updating,
    formData,
    setFormData,
    handleAssetTypeChange,
    handleCategoryChange,
    handleTriage,
    handleISIRTAnalysis,
    handleUpdate,
    loadIncidentData
  } = useIncident();

  useEffect(() => {
    if (!updating && scrollToSection) {
      const ref = scrollToSection === 'triage' ? triageSectionRef : analysisSectionRef;
      ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setScrollToSection(null); // Reset after scrolling
    }
  }, [updating, scrollToSection]);

  const handleTriageWithScroll = async () => {
    setScrollToSection('triage');
    await handleTriage();
  };

  const handleISIRTAnalysisWithScroll = async () => {
    setScrollToSection('analysis');
    await handleISIRTAnalysis();
  };

  const handleGenerateReport = () => {
    if (incident?.incident_id) {
      window.open(`/api/v1/incidents/${incident.incident_id}/report`, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <Text>Cargando detalles del incidente...</Text>
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <Text color="red">No se pudo cargar el incidente.</Text>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-6 py-8 lg:px-8 pb-16">

        <div className="grid grid-cols-1 lg:grid-cols-10 gap-8">
          {/* Left Column - Incident Details */}
          <div className="lg:col-span-7 space-y-6">
            {/* Prominent Header */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
              <div className="flex items-center gap-4">
                <div className="bg-teal-100 rounded-lg p-3">
                  <i className="fas fa-file-alt text-teal-600 text-xl"></i>
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-slate-800">Detalle del Incidente</h1>
                  <div className="mt-2">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-teal-100 text-teal-800">
                      {incident.ticket_id}
                    </span>
                  </div>
                </div>
                {/* --- Botón Actualizar movido aquí --- */}
                <div className="ml-auto flex items-center gap-x-4">
                  <Button
                    onClick={handleGenerateReport}
                    variant="secondary"
                    className="bg-white hover:bg-slate-50 text-slate-700 px-4 py-3 rounded-lg border border-slate-200 shadow-sm hover:shadow-modern-sm transition-all duration-200"
                    icon={() => <i className="fas fa-file-pdf mr-2"></i>}
                  >
                    Generar Informe
                  </Button>
                  <Button
                    onClick={handleUpdate}
                    loading={updating}
                    disabled={updating}
                    className="bg-teal-600 hover:bg-teal-700 text-white px-6 py-3 rounded-lg shadow-modern-sm hover:shadow-modern transition-all duration-200"
                    icon={() => <i className="fas fa-save mr-2"></i>}
                  >
                    Actualizar Incidente
                  </Button>
                </div>
              </div>
            </div>

            {/* Collapsible Sections */}
            <details className="bg-white rounded-lg shadow-sm border border-slate-200" open>
              <summary className="cursor-pointer p-6 font-semibold text-slate-800 hover:bg-slate-50">
                Parte I: Reporte Inicial del Incidente
              </summary>
              <div className="px-6 pb-6">
                <IncidentBasicInfo incident={incident} />
              </div>
            </details>

            <details className="bg-white rounded-lg shadow-sm border border-slate-200">
              <summary className="cursor-pointer p-6 font-semibold text-slate-800 hover:bg-slate-50">
                Parte II: Asistente de IA para Descripción
              </summary>
              <div className="px-6 pb-6">
                <IncidentAIConversation aiConversation={incident.ai_conversation} />
              </div>
            </details>

            <details className="bg-white rounded-lg shadow-sm border border-slate-200">
              <summary className="cursor-pointer p-6 font-semibold text-slate-800 hover:bg-slate-50">
                Parte III: Resumen Ejecutivo
              </summary>
              <div className="px-6 pb-6">
                <IncidentAISummary
                  summary={formData.summary}
                  description={incident.description}
                  onSummaryChange={(summary) => setFormData({ ...formData, summary })}
                />
              </div>
            </details>

            <details className="bg-white rounded-lg shadow-sm border border-slate-200">
              <summary className="cursor-pointer p-6 font-semibold text-slate-800 hover:bg-slate-50">
                Parte IV: Evidencias
              </summary>
              <div className="px-6 pb-6">
                <IncidentEvidence incidentId={incident.incident_id} evidenceFiles={incident.evidence_files} />
              </div>
            </details>

            <details className="bg-white rounded-lg shadow-sm border border-slate-200">
              <summary className="cursor-pointer p-6 font-semibold text-slate-800 hover:bg-slate-50">
                Parte V: Triaje del Incidente
              </summary>
              <div className="px-6 pb-6">
                <div ref={triageSectionRef}>
                  <IncidentTriageForm
                    users={users}
                    groups={groups}
                    categories={categories}
                    attackVectors={attackVectors}
                    assetTypes={assetTypes}
                    assets={assets}
                    incidentTypes={incidentTypes}
                    formData={formData}
                    setFormData={setFormData}
                    onAssetTypeChange={(value) => handleAssetTypeChange(parseInt(value, 10))}
                    onCategoryChange={(value) => handleCategoryChange(parseInt(value, 10))}
                    onTriage={handleTriageWithScroll}
                    isUpdating={updating}
                  />
                </div>
              </div>
            </details>

            <details className="bg-white rounded-lg shadow-sm border border-slate-200">
              <summary className="cursor-pointer p-6 font-semibold text-slate-800 hover:bg-slate-50">
                Parte VI: Análisis ISIRT
              </summary>
              <div className="px-6 pb-6">
                <div ref={analysisSectionRef}>
                  <IncidentAnalysisSection
                    formData={formData}
                    setFormData={setFormData}
                    onISIRTAnalysis={handleISIRTAnalysisWithScroll}
                    isUpdating={updating}
                  />
                  {incident.ai_recommendations?.rag_suggestion && (
                    <RAGSuggestionDisplay ragSuggestion={incident.ai_recommendations.rag_suggestion} />
                  )}
                </div>
              </div>
            </details>

            <details className="bg-white rounded-lg shadow-sm border border-slate-200">
              <summary className="cursor-pointer p-6 font-semibold text-slate-800 hover:bg-slate-50">
                Parte VII: Cierre del Incidente
              </summary>
              <div className="px-6 pb-6 space-y-6">
                <IncidentClosureSection
                  incident={incident}
                  formData={formData}
                  setFormData={setFormData}
                />
              </div>
            </details>
          </div>

          {/* Right Column - Bitácora */}
          <div className="lg:col-span-3">
            <IncidentLogTimeline
              logs={logs}
              incidentId={incident.incident_id}
              onLogAdded={loadIncidentData}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default IncidentDetailPage;
