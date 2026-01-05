
import React, { useState } from 'react';
import './Cp.css';

interface CpProps {
  id: string;
  ciudad: string;
  precio: number;
  estado: 'ACTIVE' | 'WAITING' | 'OUT_OF_SERVICE' | 'CHARGING_CENTRAL' | 'BROKEN' | 'DISCONNECTED';
}

interface Cmd {
    command: "STOP" | "START" | "BROKEN" | "UPDATE_PRICE" | "UPDATE_CITY" | "UNLINK";
    cpId: string;
    target: "ONE" | "ALL";
    driverId?: string;
    targetCharge?: number;
    newPrice?: number;
    newCity?: string;
}


const Cp: React.FC<CpProps> = ({ id, ciudad: ciudadInicial, precio: precioInicial, estado }) => {
  
  const [ciudad, setCiudad] = useState(ciudadInicial);
  const [precio, setPrecio] = useState(precioInicial);
  
  const [editandoCiudad, setEditandoCiudad] = useState(false);
  const [editandoPrecio, setEditandoPrecio] = useState(false);
  
  const [tempCiudad, setTempCiudad] = useState(ciudad);
  const [tempPrecio, setTempPrecio] = useState(precio.toString());
  
  const getEstadoColor = (estado: string): string => {
    switch (estado) {
      case 'ACTIVE':
        return '#4caf50'; // Verde
      case 'WAITING':
        return '#ff9800'; // Naranja
      case 'OUT_OF_SERVICE':
        return '#ff9800'; // Naranja
      case 'CHARGING_CENTRAL':
        return '#00ff08ff'; // Verde
      case 'BROKEN':
        return '#f44336'; // Rojo
      case 'DISCONNECTED':
        return '#9e9e9e'; // Gris
      default:
        return '#9e9e9e';
    }
  };

  const enviarComando = async (cmd: Cmd) => {
    try {
        const mutation = `
          mutation PostCommand($commandInput: CommandInput!) {
            postCommand(commandInput: $commandInput)
          }
        `;

        const response = await fetch('https://localhost:4000/graphql', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: mutation,
            variables: {
              commandInput: cmd
            }
          })
        });

        const result = await response.json();
        
        if (result.errors) {
          console.error('GraphQL errors:', result.errors);
          alert('Error al ejecutar el comando');
          return false;
        }
        
        console.log('Comando ejecutado exitosamente:', result.data);
        alert('Comando ejecutado correctamente');
        return result.data.postCommand;
    } catch (error) {
        console.error('Error al enviar el comando:', error);
        alert('Error de conexión con el servidor');
        return false;
    }
  }

  const handleParar = () => {
    console.log(`Parando CP ${id}`);
    // TODO Implementar lógica para parar 
    const cmd: Cmd = {
        command: "STOP",
        cpId: id,
        target: "ONE",
    }
    enviarComando(cmd);
  };

  const handleIniciar = async () => {
    console.log(`Iniciando CP ${id}`);
    const cmd: Cmd = {
        command: "START",
        cpId: id,
        target: "ONE",
    }
    await enviarComando(cmd);
  };

  const handleCambiarLocalizacion = () => {
    console.log(`Cambiando localización del CP ${id}`);
    setEditandoCiudad(true);
    setTempCiudad(ciudad);
  };

  const handleCambiarPrecio = () => {
    console.log(`Cambiando precio del CP ${id}`);
    setEditandoPrecio(true);
    setTempPrecio(precio.toString());
  };

  const handleDesvincular = async () => {
    console.log(`Desvinculando CP ${id}`);
    const cmd: Cmd = {
        command: "UNLINK",
        cpId: id,
        target: "ONE",
    }
    await enviarComando(cmd);
  };
  
  const guardarCiudad = async () => {
    if (tempCiudad.trim()) {
      setCiudad(tempCiudad);
      setEditandoCiudad(false);
      console.log(`Ciudad actualizada a: ${tempCiudad}`);
      
      const cmd: Cmd = {
        command: "UPDATE_CITY",
        cpId: id,
        target: "ONE",
        newCity: tempCiudad
      }
      await enviarComando(cmd);
    }
  };
  
  
  const guardarPrecio = async () => {
    const nuevoPrecio = parseFloat(tempPrecio);
    if (!isNaN(nuevoPrecio) && nuevoPrecio > 0) {
      setPrecio(nuevoPrecio);
      setEditandoPrecio(false);
      console.log(`Precio actualizado a: €${nuevoPrecio}`);
      
      const cmd: Cmd = {
        command: "UPDATE_PRICE",
        cpId: id,
        target: "ONE",
        newPrice: nuevoPrecio
      }
      await enviarComando(cmd);
    }
  };
  
  const cancelarEdicion = () => {
    setEditandoCiudad(false);
    setEditandoPrecio(false);
    setTempCiudad(ciudad);
    setTempPrecio(precio.toString());
  };

  return (
    <div 
      className="cp-card"
      style={{ 
        borderLeft: `6px solid ${getEstadoColor(estado)}`,
        backgroundColor: '#ffffff',
        borderRadius: '8px',
        padding: '16px',
        margin: '10px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        transition: 'transform 0.2s'
      }}
    >
      <div className="cp-header">
        <h3 className="cp-id">CP #{id}</h3>
        <span 
          className="cp-estado-badge"
          style={{
            backgroundColor: getEstadoColor(estado),
            color: 'white',
            padding: '4px 12px',
            borderRadius: '12px',
            fontSize: '12px',
            fontWeight: 'bold'
          }}
        >
          {estado.toUpperCase()}
        </span>
      </div>

      <div className="cp-info">
        <div className="cp-info-item">
          <strong>Ciudad:</strong> 
          {editandoCiudad ? (
            <div className="edit-field">
              <input 
                type="text" 
                value={tempCiudad}
                onChange={(e) => setTempCiudad(e.target.value)}
                className="edit-input"
                placeholder="Ciudad"
              />
              <button onClick={guardarCiudad} className="btn-save">✓</button>
              <button onClick={cancelarEdicion} className="btn-cancel">✗</button>
            </div>
          ) : (
            <span>{ciudad}</span>
          )}
        </div>
        <div className="cp-info-item">
          <strong>Precio:</strong> 
          {editandoPrecio ? (
            <div className="edit-field">
              <input 
                type="number" 
                value={tempPrecio}
                onChange={(e) => setTempPrecio(e.target.value)}
                className="edit-input"
                placeholder="Precio"
                step="0.01"
                min="0"
              />
              <span style={{ marginLeft: '4px' }}>€/kWh</span>
              <button onClick={guardarPrecio} className="btn-save">✓</button>
              <button onClick={cancelarEdicion} className="btn-cancel">✗</button>
            </div>
          ) : (
            <span>€{precio.toFixed(2)}/kWh</span>
          )}
        </div>
      </div>

      <div className="cp-actions">
        <button 
          className="btn btn-success"
          onClick={handleIniciar}
        >
          Iniciar
        </button>
        <button 
          className="btn btn-danger"
          onClick={handleParar}
        >
          Parar
        </button>
        <button 
          className="btn btn-primary"
          onClick={handleCambiarLocalizacion}
        >
          Cambiar Localización
        </button>
        <button 
          className="btn btn-warning"
          onClick={handleCambiarPrecio}
        >
          Cambiar Precio
        </button>
        <button 
          className="btn btn-secondary"
          onClick={handleDesvincular}
        >
          Desvincular
        </button>
      </div>
    </div>
  );
};

export default Cp;