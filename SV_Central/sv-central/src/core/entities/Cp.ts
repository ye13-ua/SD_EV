import { UUIDVO } from "../value-objects/UUIDVO";

export class CP {
    constructor(
        public id: UUIDVO,
        public ciudad: string,
        public calle: string,
        public precio_kwh: number
    ){}
}