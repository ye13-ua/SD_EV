import { Injectable } from '@nestjs/common';
import { CreateCommandInput } from './dto/create-command.input';
import { UpdateCommandInput } from './dto/update-command.input';

@Injectable()
export class CommandService {
  create(createCommandInput: CreateCommandInput) {
    return 'This action adds a new command';
  }

  findAll() {
    return `This action returns all command`;
  }

  findOne(id: number) {
    return `This action returns a #${id} command`;
  }

  update(id: number, updateCommandInput: UpdateCommandInput) {
    return `This action updates a #${id} command`;
  }

  remove(id: number) {
    return `This action removes a #${id} command`;
  }
}
