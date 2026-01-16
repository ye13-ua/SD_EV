import { Injectable, Logger } from '@nestjs/common';
import { Log } from './entities/log.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';

@Injectable()
export class LogService {
  private readonly logger = new Logger(LogService.name);
  
  constructor(@InjectRepository(Log)private readonly logRepository: Repository<Log>){
    this.logger.log('LogService initialized');
  }
  
  async create(description: string): Promise<Log> {
    const newLog = new Log();
    newLog.timestamp = new Date().getTime();
    newLog.description = description;
    const log = await this.logRepository.save(this.logRepository.create(newLog));
    return log;
  }

  async findAll(): Promise<Log[]> {
    this.logger.debug('Finding all log entries');
    const logs = await this.logRepository.find();
    this.logger.debug(`Found ${logs.length} log entries`);
    return logs;
  }

}
