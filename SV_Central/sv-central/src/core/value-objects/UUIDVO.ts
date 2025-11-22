import { randomUUID } from "crypto";

export class UUIDVO {
    private readonly value: string;

    constructor(uuid?: string){
        const finaluuid = uuid ?? randomUUID();

        if (!UUIDVO.isValid(finaluuid)){
            throw new Error(`Invalid UUID: ${uuid}`)
        }
        this.value = finaluuid;
    }

    static isValid(value: string): boolean {
        const uuidRegex =
            /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
        return uuidRegex.test(value);
    }

    get(): string {
        return this.value;
    }

    toString(): string {
        return this.value;
    }
}