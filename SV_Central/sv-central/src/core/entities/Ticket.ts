import { DateVO } from "../value-objects/DateVO";
import { UUIDVO } from "../value-objects/UUIDVO";

export class Ticket {
    constructor(
        public cp_id: UUIDVO, //UUID
        public driver_id: UUIDVO, //UUID
        public id: UUIDVO, //UUID
        public price: number,
        public start_time: DateVO, //TODO: Confirmar tipo date
        public end_time: DateVO
    ) {}
}