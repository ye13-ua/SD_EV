import { IsNumber, IsString, IsUUID, Min } from "class-validator"

type ActionType = "STOP" | "BROKEN" | "START" | "CHARGE" | "UPDATE_PRICE" | "UPDATE_CITY" | "DRIVER_DISCONNECT"

export class CentralCpInput {
    action: ActionType
    
    target: "ONE" | "ALL"
    
    @IsUUID()
    cpId?: string

    @IsUUID()
    driverId?: string

    @IsNumber()
    target_charge?: number
    
    @IsNumber()
    @Min(0)
    newPrice?: number

    @IsString()
    newCity?: string
}
