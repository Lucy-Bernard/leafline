import { useCallback, useEffect, useState } from "react";
import { IPlantAdapter, CreatePlantRequest } from "@/lib/types/plant.types";
import { usePlantStore } from "@/lib/store/plant.store";

export function usePlants(adapter: IPlantAdapter) {
  const { plants, isLoading, error, setPlants, addPlant, removePlant, setLoading, setError } = usePlantStore();
  const [isCreating, setIsCreating] = useState(false);

  const fetchPlants = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const fetchedPlants = await adapter.getPlants();
      setPlants(fetchedPlants);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Failed to fetch plants");
    } finally {
      setLoading(false);
    }
  }, [adapter, setPlants, setLoading, setError]);

  const createPlant = useCallback(
    async (request: CreatePlantRequest) => {
      setIsCreating(true);
      setError(null);

      try {
        const newPlant = await adapter.createPlant(request);
        addPlant(newPlant);
        return newPlant;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Failed to create plant";
        setError(errorMessage);
        throw error;
      } finally {
        setIsCreating(false);
      }
    },
    [adapter, addPlant, setError]
  );

  const deletePlant = useCallback(
    async (id: string) => {
      setError(null);

      try {
        await adapter.deletePlant(id);
        removePlant(id);
      } catch (error) {
        setError(error instanceof Error ? error.message : "Failed to delete plant");
        throw error;
      }
    },
    [adapter, removePlant, setError]
  );

  useEffect(() => {
    fetchPlants();
  }, [fetchPlants]);

  return {
    plants,
    isLoading,
    isCreating,
    error,
    fetchPlants,
    createPlant,
    deletePlant,
  };
}
