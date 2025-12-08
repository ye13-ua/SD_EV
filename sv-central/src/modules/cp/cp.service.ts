import { Injectable } from '@nestjs/common';
import { CP } from './entities/cp.entity';

@Injectable()
export class CpService {
    async getAllCps(): Promise<CP[]> {
        
        const cp1 = new CP();
        cp1.id="ID2"

        return [cp1];
    }

    async getCp(): Promise<CP> {

        const cp1 = new CP();
        cp1.id="ID2"

        return cp1;
    }


}
