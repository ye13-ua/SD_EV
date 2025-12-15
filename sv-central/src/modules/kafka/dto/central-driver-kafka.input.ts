
type ActionType = "READALL_RESPONSE" | "CONNECT_CP_RESPONSE" | "DISCONNECT" | "TICKET" | "CONNECTION_LOGS"
export class CentralDriverInput {
    action: ActionType
    driver_id?: string
    cps?: Array<{
      id: string
      ciudad: string
      calle: string
      precio: number
      estado: string
    }>
    isValidated?: boolean
    cp_id?: string
    price?: number
    logs?: string
}