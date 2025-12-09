Crear cp -> modificar uno existente si es la misma id
```graphql
mutation {
  createCp(
    cpDto: {id: "4a714f2c-7f0c-49ad-a86b-5dd69386d0d6", calle: "C/123123", ciudad: "Madrid", precio_kwh: 12.5}
  ) {
    id
    calle
    ciudad
    precio_kwh
  }
}
```
Leer cps
```graphql
{
  readAllCps {
    id
    ciudad
    calle
    precio_kwh
  }
}
```