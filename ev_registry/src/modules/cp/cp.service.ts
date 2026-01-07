import { Injectable } from '@nestjs/common';
import { CP } from './entities/cp.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { CreateCpInput } from './dto/create-cp.input';
import { UpdateCpInput } from './dto/update-cp.input';
import { randomBytes } from 'crypto';
import { BadRequestException } from '@nestjs/common';

@Injectable()
export class CpService {
	constructor(@InjectRepository(CP)private readonly cpRepository: Repository<CP>){}
	
	//---------------------------- CREATE ----------------------------
	async create(createCpInput: CreateCpInput): Promise<CP> {
		

		const clienteSecret = randomBytes(32).toString("hex");
			
		const savedCP = await this.cpRepository.save(this.cpRepository.create({...createCpInput, clientSecret: clienteSecret}))
		
		return savedCP;
	}
	
	/*
	mutation {
	createCp(
		createCpInput: {id: "a4aef408-3875-4b8f-a2a6-c4286fe836c1", ciudad: "Madrid", precio_kwh: 12.5}
	) {
		id
		ciudad
		precio_kwh
		clientSecret
		}
	}

	
	*/

	//---------------------------- READ ----------------------------
	async findAll(): Promise<CP[]> {
		return this.cpRepository.find()
	}

	async findOne(id: string): Promise<CP> {
		const dbCp = await this.cpRepository.findOne({where: {id: id}})
		
		if (!dbCp) {
			throw new BadRequestException("Cp does not exist in the db")
		}

		return dbCp
	}
	//---------------------------- UPDATE ----------------------------
	async update(updateCpInput: UpdateCpInput): Promise<CP> {
		return this.cpRepository.save(updateCpInput)
	}
	//---------------------------- DELETE ----------------------------
	async remove(id: string): Promise<boolean> {
		return (await (this.cpRepository.delete(id))).affected !== 0;
	}

	//---------------------------- UNLINK ----------------------------
	async unlinkCp(id: string): Promise<CP> {
		const dbCp = await this.cpRepository.findOne({where: {id: id}})
		if (!dbCp) {
			throw new BadRequestException("Cp does not exist in the db")
		}

		dbCp.symmetricKey = ""
		this.cpRepository.save(dbCp)

		return dbCp
	}
}