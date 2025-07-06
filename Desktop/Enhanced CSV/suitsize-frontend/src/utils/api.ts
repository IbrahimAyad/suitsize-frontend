export async function getRecommendation({ height, weight, fit, unit }: { height: number; weight: number; fit: string; unit: string }) {
  // Use the correct Railway backend URL and endpoint
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://suitsize-ai-production.up.railway.app";
  const endpoint = `${API_URL}/api/size-recommendation`;
  
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      height, 
      weight, 
      fitPreference: fit,
      unit 
    }),
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.error || `API error: ${res.status}`);
  }
  
  return await res.json();
} 