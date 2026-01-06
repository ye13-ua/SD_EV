import React, { useState, useEffect } from 'react';
import Cp from './Cp';
import './CpList.css';
import { GRAPHQL_ENDPOINT } from '../../config/api';

interface CPFromDB {
  id: string;
  ciudad: string;
  precio_kwh: number;
}

interface StatusCP {
  id?: string;
  estado?: string;
  isChanged?: boolean;
  timeStamp?: number;
  kafkaOK?: boolean;
  alreadyCharged?: number;
  driverId?: string;
  price?: number;
  city?: string;
}

interface CPCombinado {
  id: string;
  ciudad: string;
  precio: number;
  estado: 'ACTIVE' | 'WAITING' | 'OUT_OF_SERVICE' | 'CHARGING_CENTRAL' | 'BROKEN' | 'DISCONNECTED';
}

const CpList: React.FC = () => {
  const [cps, setCps] = useState<CPCombinado[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCPs = async () => {
    try {
      setLoading(true);
      
      // Query 1: Obtener todos los CPs de la base de datos
      const queryAllCPs = `
        query FindAllCps {
          findAllCps {
            id
            ciudad
            precio_kwh
          }
        }
      `;

      // Query 2: Obtener estados de CPs activos
      const queryStatusCPs = `
        query ReadAllStatusCP {
          readAllStatusCP {
            id
            estado
            city
            price
            kafkaOK
          }
        }
      `;

      // Ejecutar ambas queries
      const [responseCPs, responseStatus] = await Promise.all([
        fetch(GRAPHQL_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: queryAllCPs })
        }),
        fetch(GRAPHQL_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: queryStatusCPs })
        })
      ]);

      const resultCPs = await responseCPs.json();
      const resultStatus = await responseStatus.json();

      if (resultCPs.errors || resultStatus.errors) {
        throw new Error('Error al obtener datos del servidor');
      }

      const allCPs: CPFromDB[] = resultCPs.data.findAllCps;
      const statusCPs: StatusCP[] = resultStatus.data.readAllStatusCP;

      // Crear un mapa de estados por ID
      const statusMap = new Map<string, StatusCP>();
      statusCPs.forEach(status => {
        if (status.id) {
          statusMap.set(status.id, status);
        }
      });

      // Combinar CPs con sus estados
      const cpsCombinados: CPCombinado[] = allCPs.map(cp => {
        const status = statusMap.get(cp.id);
        
        return {
          id: cp.id,
          ciudad: status?.city || cp.ciudad,
          precio: status?.price || cp.precio_kwh,
          estado: (status?.estado as any) || 'DISCONNECTED'
        };
      });

      setCps(cpsCombinados);
      setError(null);
    } catch (err) {
      console.error('Error al cargar CPs:', err);
      setError('Error al cargar los puntos de carga');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCPs();
    
    // Actualizar cada 5 segundos
    const interval = setInterval(fetchCPs, 5000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading && cps.length === 0) {
    return (
      <div className="cp-list-container">
        <h1 className="cp-list-title">Puntos de Carga</h1>
        <p style={{ textAlign: 'center' }}>Cargando puntos de carga...</p>
      </div>
    );
  }

  if (error && cps.length === 0) {
    return (
      <div className="cp-list-container">
        <h1 className="cp-list-title">Puntos de Carga</h1>
        <p style={{ textAlign: 'center', color: 'red' }}>{error}</p>
        <button onClick={fetchCPs} style={{ display: 'block', margin: '20px auto' }}>
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="cp-list-container">
      <h1 className="cp-list-title">Puntos de Carga</h1>
      {error && (
        <div style={{ textAlign: 'center', color: 'orange', marginBottom: '10px' }}>
          {error} (mostrando última actualización exitosa)
        </div>
      )}
      <div className="cp-list-grid">
        {cps.map((cp) => (
          <Cp
            key={cp.id}
            id={cp.id}
            ciudad={cp.ciudad}
            precio={cp.precio}
            estado={cp.estado}
          />
        ))}
      </div>
      {cps.length === 0 && (
        <p style={{ textAlign: 'center' }}>No hay puntos de carga disponibles</p>
      )}
    </div>
  );
};

export default CpList;
