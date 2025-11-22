import { UUIDVO } from "../value-objects/UUIDVO";

export class Credential {
    constructor(
        public cp_id: UUIDVO,
        public jti: string,
        public expirtes_at: string, //TODO: Confirmar tipo Date
        public is_valid: boolean
    ){}
}