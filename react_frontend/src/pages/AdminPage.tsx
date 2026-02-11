import React from 'react';
import { useAdminSettings } from '../hooks/useAdminSettings';
import AiSettingsForm from '../components/admin/AiSettingsForm';
import RagSettingsForm from '../components/admin/RagSettingsForm';
import { Card, ProgressBar, Text, Button } from '@tremor/react';

const AdminPage: React.FC = () => {
  const {
    aiSettings,
    setAiSettings,
    ragSettings,
    setRagSettings,
    loading,
    ragReloading,
    showRagModal,
    setShowRagModal,
    ragProgress,
    ragStatus,
    providers,
    modelsForProvider,
    handleAiSettingsSubmit,
    handleRagSettingsSubmit,
    handleRagReload,
    handleProviderChange
  } = useAdminSettings();

  return (
    <div className="p-6 sm:p-10 space-y-10">
      <AiSettingsForm
        aiSettings={aiSettings}
        setAiSettings={setAiSettings}
        providers={providers}
        modelsForProvider={modelsForProvider}
        loading={loading}
        onSubmit={handleAiSettingsSubmit}
        onProviderChange={handleProviderChange}
      />

      <RagSettingsForm
        ragSettings={ragSettings}
        setRagSettings={setRagSettings}
        ragReloading={ragReloading}
        onSubmit={handleRagSettingsSubmit}
        onReload={handleRagReload}
      />

      {/* RAG Progress Modal */}
      {showRagModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <Card className="max-w-md w-full">
            <div className="flex items-start">
              <div className="p-2 bg-blue-100 text-blue-600 rounded-full mr-4">
                <i className="fas fa-cog fa-spin"></i>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold">Recargando Documentos RAG</h3>
                <Text className="mt-2 whitespace-pre-line">{ragStatus}</Text>
                <ProgressBar value={ragProgress} className="mt-4" />
              </div>
            </div>
            <div className="flex justify-end mt-6">
              <Button
                onClick={() => setShowRagModal(false)}
                disabled={ragReloading}
                variant="secondary"
              >
                Cerrar
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default AdminPage;
