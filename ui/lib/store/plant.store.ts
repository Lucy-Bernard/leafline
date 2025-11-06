import { create } from "zustand";
import { Plant } from "@/lib/types/plant.types";

interface PlantState {
  plants: Plant[];
  isLoading: boolean;
  error: string | null;
  setPlants: (plants: Plant[]) => void;
  addPlant: (plant: Plant) => void;
  removePlant: (id: string) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
}

export const usePlantStore = create<PlantState>((set) => ({
  plants: [],
  isLoading: false,
  error: null,
  setPlants: (plants) => set({ plants }),
  addPlant: (plant) =>
    set((state) => ({ plants: [...state.plants, plant] })),
  removePlant: (id) =>
    set((state) => ({ plants: state.plants.filter((p) => p.id !== id) })),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
}));
