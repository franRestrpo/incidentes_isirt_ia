import React from 'react';
import { useIncidentReporter } from '../hooks/useIncidentReporter';
import ChatWindow from '../components/incident/ChatWindow';
import ReportForm from '../components/incident/ReportForm';
import { Title } from '@tremor/react';

const ReportPage: React.FC = () => {
  const {
    // Chat state
    chatHistory,
    userInput,
    setUserInput,
    isAiTyping,
    onSendMessage,

    // Form state
    formData,
    setFormData,
    categories,
    severities,
    assetTypes,
    assets,
    incidentTypes,
    attackVectors,

    // Handlers
    handleAssetTypeChange,
    handleCategoryChange,
    handleAssetChange,
    handleFileChange,
    handleSubmit
  } = useIncidentReporter();

  return (
    <div className="p-6 sm:p-10">
      <Title className="mb-8">Reportar un Incidente con SecBot</Title>

      <div className="max-w-4xl mx-auto space-y-8">
        <ChatWindow
          chatHistory={chatHistory}
          userInput={userInput}
          setUserInput={setUserInput}
          isAiTyping={isAiTyping}
          onSendMessage={onSendMessage}
        />

        <ReportForm
          formData={formData}
          setFormData={setFormData}
          categories={categories}
          severities={severities}
          assetTypes={assetTypes}
          assets={assets}
          incidentTypes={incidentTypes}
          attackVectors={attackVectors}
          handleAssetTypeChange={handleAssetTypeChange}
          handleCategoryChange={handleCategoryChange}
          handleAssetChange={handleAssetChange}
          handleFileChange={handleFileChange}
          handleSubmit={handleSubmit}
        />
      </div>
    </div>
  );
};

export default ReportPage;
