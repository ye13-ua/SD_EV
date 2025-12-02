import { Test, TestingModule } from '@nestjs/testing';
import { CpResolver } from './cp.resolver';

describe('CpResolver', () => {
  let resolver: CpResolver;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [CpResolver],
    }).compile();

    resolver = module.get<CpResolver>(CpResolver);
  });

  it('should be defined', () => {
    expect(resolver).toBeDefined();
  });
});
