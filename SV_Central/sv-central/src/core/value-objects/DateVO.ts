export class DateVO {
  private readonly value: Date;

  constructor(date: Date | string | number) {
    const parsed = DateVO.parseDate(date);

    if (!(parsed instanceof Date) || isNaN(parsed.getTime())) {
      throw new Error(`Invalid date: ${date}`);
    }

    this.value = parsed;
  }

  /** Normaliza cualquier tipo de entrada a un Date */
  private static parseDate(input: Date | string | number): Date {
    if (input instanceof Date) {
      return new Date(input.getTime()); // copia para inmutabilidad
    }

    return new Date(input); // string o timestamp
  }

  /** Devuelve la fecha original (copia para no mutarla) */
  get(): Date {
    return new Date(this.value.getTime());
  }

  /** ISO string (sin perder información) */
  toISO(): string {
    return this.value.toISOString();
  }

  /** timestamp en milisegundos */
  toTimestamp(): number {
    return this.value.getTime();
  }

  /** Comparaciones útiles */
  isBefore(other: DateVO): boolean {
    return this.value < other.value;
  }

  isAfter(other: DateVO): boolean {
    return this.value > other.value;
  }

  isEqual(other: DateVO): boolean {
    return this.value.getTime() === other.value.getTime();
  }

  /** Añadir días (inmutabilidad mantenida) */
  addDays(days: number): DateVO {
    const result = new Date(this.value);
    result.setDate(result.getDate() + days);
    return new DateVO(result);
  }

  /** Restar días */
  subtractDays(days: number): DateVO {
    return this.addDays(-days);
  }

  /** Día, mes y año */
  getYear(): number {
    return this.value.getUTCFullYear();
  }

  getMonth(): number {
    return this.value.getUTCMonth() + 1; // 1–12
  }

  getDay(): number {
    return this.value.getUTCDate();
  }

  toString(): string {
    return this.toISO();
  }
}