import {
  IDiagnosisAdapter,
  DiagnosisSession,
  DiagnosisResponse,
} from "@/lib/types/diagnosis.types";
import {
  DiagnosisSessionSchema,
  DiagnosisArraySchema,
  DiagnosisResponseSchema,
} from "@/lib/schemas/diagnosis.schema";
import { API_ENDPOINTS, getAuthHeaders } from "@/lib/config/api.config";

export class DiagnosisApiAdapter implements IDiagnosisAdapter {
  async getDiagnoses(plantId: string): Promise<DiagnosisSession[]> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(API_ENDPOINTS.PLANT_DIAGNOSES(plantId), {
        method: "GET",
        headers,
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch diagnoses: ${response.statusText}`);
      }

      const data = await response.json();
      const validated = DiagnosisArraySchema.parse(data);
      return validated;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Failed to fetch diagnoses");
    }
  }

  async getDiagnosis(diagnosisId: string): Promise<DiagnosisSession> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(API_ENDPOINTS.DIAGNOSES(diagnosisId), {
        method: "GET",
        headers,
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Diagnosis with ID ${diagnosisId} not found`);
        }
        throw new Error(`Failed to fetch diagnosis: ${response.statusText}`);
      }

      const data = await response.json();
      const validated = DiagnosisSessionSchema.parse(data);
      return validated;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Failed to fetch diagnosis");
    }
  }

  async deleteDiagnosis(diagnosisId: string): Promise<void> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(API_ENDPOINTS.DIAGNOSES(diagnosisId), {
        method: "DELETE",
        headers,
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Diagnosis with ID ${diagnosisId} not found`);
        }
        throw new Error(`Failed to delete diagnosis: ${response.statusText}`);
      }
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Failed to delete diagnosis");
    }
  }

  async startDiagnosis(
    plantId: string,
    prompt: string
  ): Promise<DiagnosisResponse> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(API_ENDPOINTS.DIAGNOSES_START(plantId), {
        method: "POST",
        headers,
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Plant with ID ${plantId} not found`);
        }
        throw new Error(`Failed to start diagnosis: ${response.statusText}`);
      }

      const data = await response.json();
      const validated = DiagnosisResponseSchema.parse(data);
      return validated;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Failed to start diagnosis");
    }
  }

  async continueDiagnosis(
    diagnosisId: string,
    message: string
  ): Promise<DiagnosisResponse> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        API_ENDPOINTS.DIAGNOSES_CONTINUE(diagnosisId),
        {
          method: "PUT",
          headers,
          body: JSON.stringify({ message }),
        }
      );

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Diagnosis with ID ${diagnosisId} not found`);
        }
        if (response.status === 400) {
          const errorData = await response.json();
          throw new Error(
            errorData.detail || "Cannot update a completed diagnosis"
          );
        }
        throw new Error(
          `Failed to continue diagnosis: ${response.statusText}`
        );
      }

      const data = await response.json();
      const validated = DiagnosisResponseSchema.parse(data);
      return validated;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Failed to continue diagnosis");
    }
  }
}
