import { Injectable } from '@nestjs/common';
import { CreateRegisterInput } from './dto/create-register.input';
import { UpdateRegisterInput } from './dto/update-register.input';

@Injectable()
export class RegisterService {
  create(createRegisterInput: CreateRegisterInput) {
    return 'This action adds a new register';
  }

  findAll() {
    return `This action returns all register`;
  }

  findOne(id: number) {
    return `This action returns a #${id} register`;
  }

  update(id: number, updateRegisterInput: UpdateRegisterInput) {
    return `This action updates a #${id} register`;
  }

  remove(id: number) {
    return `This action removes a #${id} register`;
  }
}
