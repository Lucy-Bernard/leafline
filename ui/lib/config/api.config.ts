export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export const API_ENDPOINTS = {
  PLANTS: `${API_BASE_URL}/plants`,
  PLANT: (id: string) => `${API_BASE_URL}/plants/${id}`,
  PLANT_DIAGNOSES: (plantId: string) =>
    `${API_BASE_URL}/plants/${plantId}/diagnoses`,
  PLANT_CHATS: (plantId: string) => `${API_BASE_URL}/chats?plant_id=${plantId}`,
  DIAGNOSES: (diagnosisId: string) =>
    `${API_BASE_URL}/diagnoses/${diagnosisId}`,
  DIAGNOSES_START: (plantId: string) =>
    `${API_BASE_URL}/diagnoses/${plantId}`,
  DIAGNOSES_CONTINUE: (diagnosisId: string) =>
    `${API_BASE_URL}/diagnoses/${diagnosisId}`,
  CHAT_CREATE: (plantId: string) => `${API_BASE_URL}/chats?plant_id=${plantId}`,
  CHAT: (chatId: string) => `${API_BASE_URL}/chats/${chatId}`,
};

export async function getAuthHeaders(): Promise<HeadersInit> {
  if (typeof window === "undefined") {
    return {};
  }

  const { createClient } = await import("@/lib/supabase/client");
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (session?.access_token) {
    return {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    };
  }

  return {
    "Content-Type": "application/json",
  };
}
