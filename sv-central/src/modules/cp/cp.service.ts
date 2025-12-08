import { Injectable } from '@nestjs/common';
import { CP } from './entities/cp.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ID } from '@nestjs/graphql';

@Injectable()
export class CpService {
    constructor(
        @InjectRepository(CP)
        private readonly cpRepository: Repository<CP>
    ){}
    async getAllCps(): Promise<CP[]> {
        
        //const cp1 = new CP();
        //cp1.id="ID2"


        return this.cpRepository.find()
        //return [cp1];
    }

    async getCp(id: string): Promise<CP> {

        const cp1 = new CP();
        cp1.id="ID2"
        //return this.cpRepository.findOne({where: {id: id}})
        return cp1;
    }


}
