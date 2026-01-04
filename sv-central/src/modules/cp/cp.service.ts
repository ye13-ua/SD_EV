import { Injectable } from '@nestjs/common';
import { CP } from './entities/cp.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { RegisterCpInput } from './dto/register-cp.input';
import { UpdateCpInput } from './dto/update-cp.input';
import { randomBytes } from 'crypto';
import { compare } from "bcrypt"
import { UnauthorizedException, BadRequestException } from '@nestjs/common';

@Injectable()
export class CpService {
	constructor(@InjectRepository(CP)private readonly cpRepository: Repository<CP>){}
	
	//---------------------------- AUTETICATE ----------------------------
	async auteticateCp(registerCpInput: RegisterCpInput): Promise<CP> {
		
		const dbCp = await this.cpRepository.findOne({where: {id: registerCpInput.id}})
		//TODO borrar
		
		if (!dbCp){
			throw new UnauthorizedException('Bad credentials');
		}

		const isValid = await compare(registerCpInput.clientSecret, dbCp.clientSecretHash)
		
		if (!isValid) {
			throw new UnauthorizedException('Bad credentials');
		}

		dbCp.symmetricKey = randomBytes(32).toString("hex");
		this.cpRepository.save(dbCp)
		return dbCp
		
	}

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

	//---------------------------- UNLINK ----------------------------
	async unlink(id: string): Promise<boolean> {
		
		const dbCp = await this.cpRepository.findOne({where: {id: id}})
		
		if (!dbCp) {
			throw new BadRequestException("Cp does not exist in the db")
		}
		
		dbCp.symmetricKey = ""
		this.cpRepository.save(dbCp)

		return true
	}
	//---------------------------- UPDATE ----------------------------
	async update(updateCpInput: UpdateCpInput): Promise<CP> {
		return this.cpRepository.save(updateCpInput)
	}
}
