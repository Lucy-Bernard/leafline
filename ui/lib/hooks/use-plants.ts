// Fetches and manages the user's plant collection.
// State lives in the Zustand plant store (not local state) so it persists if the
// component unmounts and remounts without needing to re-fetch from the API.
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
      try {
        const newPlant = await adapter.createPlant(request);
        addPlant(newPlant);
        return newPlant;
      } catch (error) {
        // Don't write to the global store error — creation errors are shown
        // inline inside the dialog. Writing here hides the plant grid on the
        // dashboard and breaks the Dashboard nav link (already on the same route).
        throw error;
      } finally {
        setIsCreating(false);
      }
    },
    [adapter, addPlant]
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
