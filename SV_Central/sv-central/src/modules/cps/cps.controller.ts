import { Controller, Get } from '@nestjs/common';
import { CpsService } from './cps.service';

//cps

@Controller('cps')
export class CpsController {
    constructor(private readonly cpsService: CpsService) {}

    @Get()
    readAll() {
        
    }
}
