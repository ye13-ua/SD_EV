export const KafkaTopics = {
    CENTRAL_DRIVER_COMMANDS: process.env.CENTRAL_DRIVER_COMMANDS ?? "Central.Driver.Commands",
    CENTRAL_CP_COMMANDS: process.env.CENTRAL_CP_COMMANDS ?? "Central.CP.Commands",
    DRIVER_COMMANDS: process.env.DRIVER_COMMANDS ?? "Driver.Commands"
}