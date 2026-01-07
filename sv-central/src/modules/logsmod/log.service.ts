import { Injectable, Logger } from '@nestjs/common';
import { CreateLogInput } from './dto/create-log.input';
import { Log } from './entities/log.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';

@Injectable()
export class LogService {
  private readonly logger = new Logger(LogService.name);
  
  constructor(@InjectRepository(Log)private readonly logRepository: Repository<Log>){
    this.logger.log('LogService initialized');
  }
  
  async create(createLogInput: CreateLogInput): Promise<Log> {
    this.logger.log(`Creating log entry: ${createLogInput.description?.substring(0, 50) || 'no description'}`);
    const log = await this.logRepository.save(this.logRepository.create(createLogInput));
    this.logger.debug(`Log entry created with timestamp: ${log.timestamp}`);
    return log;
  }

  async findAll(): Promise<Log[]> {
    this.logger.debug('Finding all log entries');
    const logs = await this.logRepository.find();
    this.logger.debug(`Found ${logs.length} log entries`);
    return logs;
  }

}
