import { IPlantAdapter, Plant, CreatePlantRequest } from "@/lib/types/plant.types";
import { PlantSchema, PlantArraySchema } from "@/lib/schemas/plant.schema";
import { API_ENDPOINTS, getAuthHeaders } from "@/lib/config/api.config";

export class PlantApiAdapter implements IPlantAdapter {
  async getPlants(): Promise<Plant[]> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(API_ENDPOINTS.PLANTS, {
        method: "GET",
        headers,
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch plants: ${response.statusText}`);
      }

      const data = await response.json();
      const validated = PlantArraySchema.parse(data);
      return validated;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Failed to fetch plants");
    }
  }

  async getPlant(id: string): Promise<Plant> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(API_ENDPOINTS.PLANT(id), {
        method: "GET",
        headers,
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Plant with ID ${id} not found`);
        }
        throw new Error(`Failed to fetch plant: ${response.statusText}`);
      }

      const data = await response.json();
      const validated = PlantSchema.parse(data);
      return validated;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Failed to fetch plant");
    }
  }

  async createPlant(request: CreatePlantRequest): Promise<Plant> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(API_ENDPOINTS.PLANTS, {
        method: "POST",
        headers,
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to create plant: ${response.statusText}`);
      }

      const data = await response.json();
      const validated = PlantSchema.parse(data);
      return validated;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Failed to create plant");
    }
  }

  async deletePlant(id: string): Promise<void> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(API_ENDPOINTS.PLANT(id), {
        method: "DELETE",
        headers,
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Plant with ID ${id} not found`);
        }
        throw new Error(`Failed to delete plant: ${response.statusText}`);
      }
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("Failed to delete plant");
    }
  }
}
