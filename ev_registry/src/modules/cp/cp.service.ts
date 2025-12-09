import { Injectable } from '@nestjs/common';
import { CP } from './entities/cp.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { CreateCpDto } from './dto/create-cp.dto';


@Injectable()
export class CpService {
    constructor(@InjectRepository(CP)private readonly cpRepository: Repository<CP>){}
    
    //---------------------------- CREATE ----------------------------
    async createCP(cpDto: CreateCpDto): Promise<CP> {
        const newCP = this.cpRepository.create(cpDto);
        return await this.cpRepository.save(newCP)
    }

    //---------------------------- READ ----------------------------
    async readAllCps(): Promise<CP[]> {
        return this.cpRepository.find()
    }

    async readCp(id: string): Promise<CP> {
        return this.cpRepository.findOneOrFail({where: {id: id}})
    }
    //---------------------------- UPDATE ----------------------------

    //---------------------------- DELETE ----------------------------
}
