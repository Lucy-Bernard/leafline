import { z } from "zod";

export const DiagnosisMessageSchema = z.object({
  role: z.enum(["user", "assistant"]),
  message: z.string(),
});

export const DiagnosisResultSchema = z.object({
  finding: z.string(),
  recommendation: z.string(),
});

export const DiagnosisContextSchema = z.object({
  initial_prompt: z.string(),
  conversation_history: z.array(DiagnosisMessageSchema),
  state: z.record(z.string(), z.unknown()).optional(),
  plant_vitals: z
    .object({
      name: z.string(),
      care_schedule: z
        .object({
          care_instructions: z.string(),
          watering_schedule: z.string(),
        })
        .optional(),
    })
    .optional(),
  result: DiagnosisResultSchema.optional(),
});

export const DiagnosisSessionSchema = z.object({
  id: z.string(),
  plant_id: z.string(),
  status: z.enum(["PENDING_USER_INPUT", "COMPLETED", "CANCELLED"]),
  diagnosis_context: DiagnosisContextSchema,
  created_at: z.string(),
  updated_at: z.string(),
});

export const DiagnosisArraySchema = z.array(DiagnosisSessionSchema);

export const DiagnosisResponseSchema = z.object({
  diagnosis_id: z.string(),
  status: z.enum(["PENDING_USER_INPUT", "COMPLETED"]),
  ai_question: z.string().optional(),
  result: DiagnosisResultSchema.optional(),
});
