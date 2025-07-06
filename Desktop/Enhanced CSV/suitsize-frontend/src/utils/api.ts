export async function getRecommendation({ height, weight, fit, unit }: { height: number; weight: number; fit: string; unit: string }) {
  // Replace with your actual Railway backend URL
  const API_URL = "https://your-railway-app.up.railway.app/recommend";
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ height, weight, fit, unit }),
  });
  if (!res.ok) throw new Error("API error");
  return await res.json();
} 