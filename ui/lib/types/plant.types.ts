export interface CareSchedule {
  care_instructions: string;
  watering_schedule: string;
}

export interface Plant {
  id: string;
  user_id: string;
  name: string;
  care_schedule: CareSchedule;
  image_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreatePlantRequest {
  image: string;
  latitude?: number;
  longitude?: number;
  similar_images?: boolean;
}

export interface IPlantAdapter {
  getPlants(): Promise<Plant[]>;
  getPlant(id: string): Promise<Plant>;
  createPlant(request: CreatePlantRequest): Promise<Plant>;
  deletePlant(id: string): Promise<void>;
}
