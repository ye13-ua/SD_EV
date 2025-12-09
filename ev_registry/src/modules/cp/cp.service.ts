import { Injectable } from '@nestjs/common';
import { CP } from './entities/cp.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { DeleteResult, Repository } from 'typeorm';
import { CreateCpDto } from './dto/create-cp.input';
import { UpdateCpDto } from './dto/update-cp.input';
import { skip } from 'node:test';


@Injectable()
export class CpService {
    constructor(@InjectRepository(CP)private readonly cpRepository: Repository<CP>){}
    
    //---------------------------- CREATE ----------------------------
    async createCP(createCpDto: CreateCpDto): Promise<CP> {
        const newCP = this.cpRepository.create(createCpDto);
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
    async updateCp(updateCpDto: UpdateCpDto): Promise<CP> {

        return this.cpRepository.save(updateCpDto)
    }
    //---------------------------- DELETE ----------------------------
    async deleteCp(id: string): Promise<boolean> {
        
        return (await (this.cpRepository.delete(id))).affected !== 0;
    }


}
