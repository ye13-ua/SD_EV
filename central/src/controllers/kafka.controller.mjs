export * from "./kafka.consumer.controller.mjs"
export * from "./kafka.producer.controller.mjs"

import { Kafka } from "kafkajs";

const kafkaInstance = new Kafka({
    clientId: "EV_Central",
    brokers: [process.env.KAFKA_BOOTSTRAP],
  })

    
export async function ensureTopic(topic) {
  const admin = kafkaInstance.admin();
  await admin.connect();
  const topics = await admin.listTopics();

  if (!topics.includes(topic)) {
    await admin.createTopics({ topics: [{ topic }] });
    console.log(`Topico "${topic}" creado.`);
  }

  await admin.disconnect();
}