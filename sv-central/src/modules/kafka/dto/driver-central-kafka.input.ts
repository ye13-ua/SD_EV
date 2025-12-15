type ActionType = "READALL" | "CONNECTCP" | "DISCONNECT" | "REGISTER"
export class DriverCentralInput {
    action: ActionType
    driver_id: string
    cp_id?: string
    charge?: number
}