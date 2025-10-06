/**
 * Funcionamiento como microservicios
 * indexJS se encarga de recibir datos y enviarselos a index.html
 * Tiene que recibir los datos de esta estructura json:
 * TIene que tener las siguientes funcionalidades:
 * 
 * POST en (http://ip:3000/CPs)
 * GET en (http://ip:3000/CPs)
 * UPDATE en (http://ip:3000/CPs/:id)
 * DELETE en (http://ip:3000/CPs/:id)
 * [{
 *    ID_UUID: String
 *    State: int
 *    Ubicacion: string
 *    Precio: double (KW/H)
 * }]
 * 
 * No va a tener validaciones ()
 * Solo es accesible desde la red de docker -> ev_net y localhost
 * 
 */

import express from "express";

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.disable("x-powered-by");

app.post("/CPs",(req,res) => {
  const CPs = req.body;
  if (!Array.isArray(CPs)) { 
    return res.status(400).json({ok: false, error: "Los datos recibidos no tienen estructura correcta"})
  }

})

app.get("/", (req, res) => {
  res.send("Hola mundo");
});

app.listen(PORT, () => {
  console.log(`Servidor escuchando en el puerto ${PORT}`);
});