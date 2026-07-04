// Fetches and manages the user's plant collection.
// Local state, scoped to wherever this hook is called (currently just the dashboard).
import { useCallback, useEffect, useState } from "react";
import { IPlantAdapter, CreatePlantRequest, Plant } from "@/lib/types/plant.types";

export function usePlants(adapter: IPlantAdapter) {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [isLoading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
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
  }, [adapter]);

  const createPlant = useCallback(
    async (request: CreatePlantRequest) => {
      setIsCreating(true);
      try {
        const newPlant = await adapter.createPlant(request);
        setPlants((prev) => [...prev, newPlant]);
        return newPlant;
      } catch (error) {
        // Don't write to `error` here — creation errors are shown inline
        // inside the dialog instead of hiding the plant grid on the dashboard.
        throw error;
      } finally {
        setIsCreating(false);
      }
    },
    [adapter]
  );

  const deletePlant = useCallback(
    async (id: string) => {
      setError(null);

      try {
        await adapter.deletePlant(id);
        setPlants((prev) => prev.filter((p) => p.id !== id));
      } catch (error) {
        setError(error instanceof Error ? error.message : "Failed to delete plant");
        throw error;
      }
    },
    [adapter]
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
