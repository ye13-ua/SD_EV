import { Injectable, Logger } from '@nestjs/common';
import { CP } from './entities/cp.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { RegisterCpInput } from './dto/register-cp.input';
import { UpdateCpInput } from './dto/update-cp.input';
import { randomBytes } from 'crypto';
import { UnauthorizedException, BadRequestException } from '@nestjs/common';

@Injectable()
export class CpService {
	private readonly logger = new Logger(CpService.name);
	
	constructor(@InjectRepository(CP)private readonly cpRepository: Repository<CP>){
		this.logger.log('CpService initialized');
	}
	
	//---------------------------- AUTHENTICATE ----------------------------
	async authenticateCp(registerCpInput: RegisterCpInput): Promise<CP> {
		this.logger.log(`Authenticating CP: ${registerCpInput.id}`);

		const dbCp = await this.cpRepository.findOne({where: {id: registerCpInput.id}});
		
		if (!dbCp){
			this.logger.error(`Authentication failed - CP not found: ${registerCpInput.id}`);
			throw new UnauthorizedException('Bad credentials');
		}

		const isValid = dbCp.clientSecret === registerCpInput.clientSecret;
		
		if (!isValid) {
			this.logger.error(`Authentication failed - Invalid secret for CP: ${registerCpInput.id}`);
			throw new UnauthorizedException('Bad credentials');
		}

		dbCp.symmetricKey = randomBytes(32).toString("hex");
		await this.cpRepository.save(dbCp);
		this.logger.log(`CP authenticated successfully: ${registerCpInput.id}`);
		return dbCp;
	}

	//---------------------------- READ ----------------------------
	async findAll(): Promise<CP[]> {
		this.logger.debug('Finding all CPs');
		const cps = await this.cpRepository.find();
		this.logger.debug(`Found ${cps.length} CPs`);
		return cps;
	}

	async findOne(id: string): Promise<CP> {
		this.logger.debug(`Finding CP: ${id}`);
		 
		const dbCp = await this.cpRepository.findOne({where: {id: id}});
		
		if (!dbCp) {
			this.logger.error(`CP not found: ${id}`);
			throw new BadRequestException("Cp does not exist in the db");
		}

		this.logger.debug(`CP found: ${id}`);
		return dbCp;
	}

	//---------------------------- UNLINK ----------------------------
	async unlink(id: string): Promise<boolean> {
		this.logger.log(`Unlinking CP: ${id}`);
		
		const dbCp = await this.cpRepository.findOne({where: {id: id}});
		
		if (!dbCp) {
			this.logger.error(`Cannot unlink - CP not found: ${id}`);
			throw new BadRequestException("Cp does not exist in the db");
		}
		
		dbCp.symmetricKey = "";
		await this.cpRepository.save(dbCp);
		this.logger.log(`CP unlinked successfully: ${id}`);

		return true;
	}
	//---------------------------- UPDATE ----------------------------
	async update(updateCpInput: UpdateCpInput): Promise<CP> {
		this.logger.log(`Updating CP: ${updateCpInput.id}`);
		const updated = await this.cpRepository.save(updateCpInput);
		this.logger.log(`CP updated successfully: ${updateCpInput.id}`);
		return updated;
	}
}
