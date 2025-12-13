import { Injectable } from '@nestjs/common';
import { CP } from './entities/cp.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { CreateCpInput } from './dto/create-cp.input';
import { UpdateCpInput } from './dto/update-cp.input';
import { randomBytes } from 'crypto';
import { hash } from "argon2";



@Injectable()
export class CpService {
	constructor(@InjectRepository(CP)private readonly cpRepository: Repository<CP>){}
	
	//---------------------------- CREATE ----------------------------
	async create(createCpInput: CreateCpInput): Promise<CP> {
		

		const clienteSecret = randomBytes(32).toString("hex");
		const clientSecretHash = await hash(clienteSecret)
		createCpInput.clientSecretHash = clientSecretHash;

		const savedCP = await this.cpRepository.save(this.cpRepository.create(createCpInput))
		
		savedCP.clientSecret = clienteSecret;
		return savedCP;
	}

	//---------------------------- READ ----------------------------
	async findAll(): Promise<CP[]> {
		return this.cpRepository.find()
	}

	async findOne(id: string): Promise<CP> {
		return this.cpRepository.findOneOrFail({where: {id: id}})
	}
	//---------------------------- UPDATE ----------------------------
	async update(updateCpInput: UpdateCpInput): Promise<CP> {
		return this.cpRepository.save(updateCpInput)
	}

	//---------------------------- DELETE ----------------------------
	async remove(id: string): Promise<boolean> {
		return (await (this.cpRepository.delete(id))).affected !== 0;
	}
}
