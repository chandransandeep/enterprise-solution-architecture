// Example client. Replace the key with a non-production, local key.
const response = await fetch('http://localhost:8000/v1/vacancies', {
  headers: { 'X-API-Key': process.env.DEMO_API_KEY ?? 'local-development-only' }
});
if (!response.ok) throw new Error(`API returned ${response.status}`);
console.log(await response.json());
