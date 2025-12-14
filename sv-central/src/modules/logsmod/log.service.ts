import { Injectable } from '@nestjs/common';
import { CreateLogInput } from './dto/create-log.input';
import { Log } from './entities/log.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';

@Injectable()
export class LogService {
  constructor(@InjectRepository(Log)private readonly logRepository: Repository<Log>){}
  
  async create(createLogInput: CreateLogInput): Promise<Log> {
    return await this.logRepository.save(this.logRepository.create(createLogInput))  
  }

  async findAll(): Promise<Log[]> {
    return this.logRepository.find()
  }

}
