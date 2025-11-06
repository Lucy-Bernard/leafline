import { z } from "zod";

export const CareScheduleSchema = z.object({
  care_instructions: z.string(),
  watering_schedule: z.string(),
});

export const PlantSchema = z.object({
  id: z.string(),
  user_id: z.string(),
  name: z.string(),
  care_schedule: CareScheduleSchema,
  image_url: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const PlantArraySchema = z.array(PlantSchema);

export type PlantSchemaType = z.infer<typeof PlantSchema>;
