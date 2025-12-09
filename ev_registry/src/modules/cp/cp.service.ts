import { Injectable } from '@nestjs/common';
import { CP } from './entities/cp.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { CreateCpDto } from './dto/create-cp.dto';


@Injectable()
export class CpService {
    constructor(@InjectRepository(CP)private readonly cpRepository: Repository<CP>){}
    
    async createCP(cpDto: CreateCpDto): Promise<CP> {
        const newCP = this.cpRepository.create(cpDto);

        return await this.cpRepository.save(newCP)
    }


    async readAllCps(): Promise<CP[]> {

        return this.cpRepository.find()
    }

    async readCp(id: string): Promise<CP> {

        const cp1 = new CP();
        cp1.id="ID2"
        //return this.cpRepository.findOne({where: {id: id}})
        return cp1;
    }



}
