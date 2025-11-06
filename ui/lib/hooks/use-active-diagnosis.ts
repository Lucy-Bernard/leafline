import { useCallback, useState } from "react";
import {
  IDiagnosisAdapter,
  DiagnosisMessage,
  DiagnosisResult,
} from "@/lib/types/diagnosis.types";

type DiagnosisStatus =
  | "idle"
  | "loading"
  | "pending_input"
  | "completed"
  | "error";

export function useActiveDiagnosis(
  adapter: IDiagnosisAdapter,
  plantId: string
) {
  const [messages, setMessages] = useState<DiagnosisMessage[]>([]);
  const [status, setStatus] = useState<DiagnosisStatus>("idle");
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const [diagnosisId, setDiagnosisId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startDiagnosis = useCallback(
    async (prompt: string) => {
      setStatus("loading");
      setError(null);
      setMessages([]);
      setResult(null);

      try {
        const userMessage: DiagnosisMessage = {
          role: "user",
          message: prompt,
        };
        setMessages([userMessage]);

        const response = await adapter.startDiagnosis(plantId, prompt);
        setDiagnosisId(response.diagnosis_id);

        if (response.status === "COMPLETED" && response.result) {
          setResult(response.result);
          setStatus("completed");
        } else if (response.ai_question) {
          const aiMessage: DiagnosisMessage = {
            role: "assistant",
            message: response.ai_question,
          };
          setMessages((prev) => [...prev, aiMessage]);
          setStatus("pending_input");
        }
      } catch (error) {
        setError(
          error instanceof Error ? error.message : "Failed to start diagnosis"
        );
        setStatus("error");
      }
    },
    [adapter, plantId]
  );

  const sendMessage = useCallback(
    async (message: string) => {
      if (!diagnosisId) {
        setError("No active diagnosis session");
        setStatus("error");
        return;
      }

      setStatus("loading");
      setError(null);

      try {
        const userMessage: DiagnosisMessage = {
          role: "user",
          message,
        };
        setMessages((prev) => [...prev, userMessage]);

        const response = await adapter.continueDiagnosis(diagnosisId, message);

        if (response.status === "COMPLETED" && response.result) {
          setResult(response.result);
          setStatus("completed");
        } else if (response.ai_question) {
          const aiMessage: DiagnosisMessage = {
            role: "assistant",
            message: response.ai_question,
          };
          setMessages((prev) => [...prev, aiMessage]);
          setStatus("pending_input");
        }
      } catch (error) {
        setError(
          error instanceof Error
            ? error.message
            : "Failed to continue diagnosis"
        );
        setStatus("error");
      }
    },
    [adapter, diagnosisId]
  );

  const reset = useCallback(() => {
    setMessages([]);
    setStatus("idle");
    setResult(null);
    setDiagnosisId(null);
    setError(null);
  }, []);

  return {
    messages,
    status,
    result,
    error,
    diagnosisId,
    startDiagnosis,
    sendMessage,
    reset,
  };
}
