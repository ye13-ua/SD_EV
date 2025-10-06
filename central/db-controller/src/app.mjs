/**
 * MODULO X
 * CONTROLADOR V
 * ENRUTADOR X
 * ESQUEMA V
 * CONFIG
 */


import express from "express";

const app = express();
const PORT = process.env.PORT || 4000;

app.use(express.json());
app.disable("x-powered-by");

app.get("/", (req, res) => {
  res.send("Hola mundo");
});

app.listen(PORT, () => {
  console.log(`Servidor escuchando en el puerto ${PORT}`);
});