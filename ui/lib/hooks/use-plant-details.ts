import { useCallback, useEffect, useState } from "react";
import { IPlantAdapter, Plant } from "@/lib/types/plant.types";

export function usePlantDetails(adapter: IPlantAdapter, plantId: string) {
  const [plant, setPlant] = useState<Plant | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPlant = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const fetchedPlant = await adapter.getPlant(plantId);
      setPlant(fetchedPlant);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Failed to fetch plant"
      );
    } finally {
      setIsLoading(false);
    }
  }, [adapter, plantId]);

  useEffect(() => {
    fetchPlant();
  }, [fetchPlant]);

  return {
    plant,
    isLoading,
    error,
    refetch: fetchPlant,
  };
}
