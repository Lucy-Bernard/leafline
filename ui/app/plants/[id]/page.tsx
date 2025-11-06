"use client";

import { useState } from "react";
import { usePlantDetails } from "@/lib/hooks/use-plant-details";
import { useDiagnoses } from "@/lib/hooks/use-diagnoses";
import { useChats } from "@/lib/hooks/use-chats";
import { useActiveDiagnosis } from "@/lib/hooks/use-active-diagnosis";
import { useActiveChat } from "@/lib/hooks/use-active-chat";
import { PlantApiAdapter } from "@/lib/adapters/plant-api.adapter";
import { DiagnosisApiAdapter } from "@/lib/adapters/diagnosis-api.adapter";
import { ChatApiAdapter } from "@/lib/adapters/chat-api.adapter";
import { PlantInfoHeader } from "@/components/feature/plant-info-header";
import { DiagnosisHistory } from "@/components/feature/diagnosis-history";
import { ChatHistory } from "@/components/feature/chat-history";
import { StartDiagnosisDialog } from "@/components/feature/start-diagnosis-dialog";
import { StartChatDialog } from "@/components/feature/start-chat-dialog";
import { ActiveDiagnosisPanel } from "@/components/feature/active-diagnosis-panel";
import { ActiveChatPanel } from "@/components/feature/active-chat-panel";
import { DiagnosisResultDisplay } from "@/components/feature/diagnosis-result-display";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

const plantAdapter = new PlantApiAdapter();
const diagnosisAdapter = new DiagnosisApiAdapter();
const chatAdapter = new ChatApiAdapter();

export default function PlantInfoPage() {
  const params = useParams();
  const router = useRouter();
  const plantId = params.id as string;
  const [showResult, setShowResult] = useState(false);

  const {
    plant,
    isLoading: isLoadingPlant,
    error: plantError,
  } = usePlantDetails(plantAdapter, plantId);

  const {
    diagnoses,
    isLoading: isLoadingDiagnoses,
    deleteDiagnosis,
    refetch: refetchDiagnoses,
  } = useDiagnoses(diagnosisAdapter, plantId);

  const {
    chats,
    isLoading: isLoadingChats,
    deleteChat,
    refetch: refetchChats,
  } = useChats(chatAdapter, plantId);

  const {
    messages,
    status,
    result,
    error: diagnosisError,
    startDiagnosis,
    sendMessage,
    reset,
  } = useActiveDiagnosis(diagnosisAdapter, plantId);

  const {
    messages: chatMessages,
    status: chatStatus,
    error: chatError,
    startChat,
    sendMessage: sendChatMessage,
    reset: resetChat,
  } = useActiveChat(chatAdapter, plantId);

  const handleStartDiagnosis = async (prompt: string) => {
    await startDiagnosis(prompt);
  };

  const handleCancelDiagnosis = () => {
    reset();
    setShowResult(false);
  };

  const handleCompleteDiagnosis = () => {
    setShowResult(true);
  };

  const handleCloseDiagnosisResult = () => {
    reset();
    setShowResult(false);
    refetchDiagnoses();
  };

  const handleStartChat = async (content: string) => {
    await startChat(content);
  };

  const handleCancelChat = () => {
    resetChat();
    refetchChats();
  };

  if (plantError) {
    return (
      <div className="flex-1 w-full flex flex-col gap-12">
        <Button
          variant="ghost"
          onClick={() => router.push("/dashboard")}
          className="w-fit"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
        <div
          className="bg-destructive/10 text-destructive px-4 py-3 rounded"
          data-testid="error-message"
        >
          <p className="font-semibold">Error loading plant</p>
          <p className="text-sm">{plantError}</p>
        </div>
      </div>
    );
  }

  if (isLoadingPlant) {
    return (
      <div className="flex-1 w-full flex flex-col gap-12">
        <Skeleton className="h-12 w-32" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!plant) {
    return (
      <div className="flex-1 w-full flex flex-col gap-12">
        <Button
          variant="ghost"
          onClick={() => router.push("/dashboard")}
          className="w-fit"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
        <div className="text-center py-12">
          <p className="text-muted-foreground">Plant not found</p>
        </div>
      </div>
    );
  }

  const startDiagnosisButton = status === "idle" && chatStatus === "idle" && (
    <StartDiagnosisDialog onStart={handleStartDiagnosis} />
  );

  const startChatButton = status === "idle" && chatStatus === "idle" && (
    <StartChatDialog onStart={handleStartChat} />
  );

  if (showResult && result) {
    return (
      <div className="flex-1 w-full flex flex-col gap-8">
        <Button
          variant="ghost"
          onClick={() => router.push("/dashboard")}
          className="w-fit"
          data-testid="back-button"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>

        <PlantInfoHeader plant={plant} actionButton={startDiagnosisButton} />

        <DiagnosisResultDisplay
          result={result}
          onClose={handleCloseDiagnosisResult}
        />
      </div>
    );
  }

  if (status !== "idle") {
    return (
      <div className="flex-1 w-full flex flex-col gap-8">
        <Button
          variant="ghost"
          onClick={() => router.push("/dashboard")}
          className="w-fit"
          data-testid="back-button"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>

        <PlantInfoHeader plant={plant} actionButton={startDiagnosisButton} />

        <ActiveDiagnosisPanel
          messages={messages}
          status={status}
          error={diagnosisError}
          result={result}
          onSendMessage={sendMessage}
          onCancel={handleCancelDiagnosis}
          onComplete={handleCompleteDiagnosis}
        />
      </div>
    );
  }

  if (chatStatus !== "idle") {
    return (
      <div className="flex-1 w-full flex flex-col gap-8">
        <Button
          variant="ghost"
          onClick={() => router.push("/dashboard")}
          className="w-fit"
          data-testid="back-button"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>

        <PlantInfoHeader plant={plant} actionButton={startChatButton} />

        <ActiveChatPanel
          messages={chatMessages}
          status={chatStatus}
          error={chatError}
          onSendMessage={sendChatMessage}
          onCancel={handleCancelChat}
        />
      </div>
    );
  }

  return (
    <div className="flex-1 w-full flex flex-col gap-8">
      <Button
        variant="ghost"
        onClick={() => router.push("/dashboard")}
        className="w-fit"
        data-testid="back-button"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to Dashboard
      </Button>

      <PlantInfoHeader plant={plant} actionButton={startDiagnosisButton} />

      <Tabs defaultValue="diagnoses" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="diagnoses" data-testid="diagnoses-tab">
            Diagnosis History
          </TabsTrigger>
          <TabsTrigger value="chats" data-testid="chats-tab">
            Chat History
          </TabsTrigger>
        </TabsList>

        <TabsContent value="diagnoses" className="mt-6">
          <DiagnosisHistory
            diagnoses={diagnoses}
            isLoading={isLoadingDiagnoses}
            onDelete={deleteDiagnosis}
          />
        </TabsContent>

        <TabsContent value="chats" className="mt-6">
          <div className="space-y-4">
            <div className="flex justify-end">{startChatButton}</div>
            <ChatHistory
              chats={chats}
              isLoading={isLoadingChats}
              onDelete={deleteChat}
            />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
