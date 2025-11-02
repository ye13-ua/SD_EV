import z from "zod"

const CPSchema = z.object({
    ID_UUID: z.uuid(),
    Ubicacion: z.string(),
    UbicacionLarga: z.string(),
    Precio_KWH: z.float32()
})

export function validateCP(object) {
    return CPSchema.safeParse(object);
}

export function validateParcialCP(object) {
    return CPSchema.partial().safeParse(object);
}