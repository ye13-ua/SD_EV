// Configuración de la URL base de la API
// Si existe VITE_CENTRAL_URL (en Docker), usar esa URL
// Si no, usar localhost:4000 (desarrollo local)
const getCentralUrl = (): string => {
  const centralUrl = import.meta.env.VITE_CENTRAL_URL;
  
  if (centralUrl) {
    // En Docker, usar el nombre del contenedor
    return centralUrl;
  }
  
  // En desarrollo local, usar localhost
  return 'https://localhost:4000';
};

export const API_BASE_URL = getCentralUrl();
export const GRAPHQL_ENDPOINT = `${API_BASE_URL}/graphql`;
