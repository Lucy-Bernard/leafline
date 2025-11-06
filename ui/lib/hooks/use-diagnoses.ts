import { useCallback, useEffect, useState } from "react";
import {
  IDiagnosisAdapter,
  DiagnosisSession,
} from "@/lib/types/diagnosis.types";

export function useDiagnoses(adapter: IDiagnosisAdapter, plantId: string) {
  const [diagnoses, setDiagnoses] = useState<DiagnosisSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDiagnoses = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const fetchedDiagnoses = await adapter.getDiagnoses(plantId);
      const sortedDiagnoses = [...fetchedDiagnoses].sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setDiagnoses(sortedDiagnoses);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Failed to fetch diagnoses"
      );
    } finally {
      setIsLoading(false);
    }
  }, [adapter, plantId]);

  const deleteDiagnosis = useCallback(
    async (diagnosisId: string) => {
      setError(null);

      try {
        await adapter.deleteDiagnosis(diagnosisId);
        setDiagnoses((prev) => prev.filter((d) => d.id !== diagnosisId));
      } catch (error) {
        setError(
          error instanceof Error ? error.message : "Failed to delete diagnosis"
        );
        throw error;
      }
    },
    [adapter]
  );

  useEffect(() => {
    fetchDiagnoses();
  }, [fetchDiagnoses]);

  return {
    diagnoses,
    isLoading,
    error,
    deleteDiagnosis,
    refetch: fetchDiagnoses,
  };
}
