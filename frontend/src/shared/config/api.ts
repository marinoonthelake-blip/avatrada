export const getApiBaseUrl = () => {
  const wsUrl = import.meta.env.VITE_API_BASE_URL;
  // Convert ws://100.x.x.x:8000 to http://100.x.x.x:8000
  return wsUrl.replace('ws://', 'http://').replace('wss://', 'https://');
};
