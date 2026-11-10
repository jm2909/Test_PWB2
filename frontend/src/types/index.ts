export interface ListResponse<T> {
  items: T[];
  total: number;
}

export type * from './onboarding';
export type * from './consent';
export type * from './device';
export type * from './goal';
export type * from './sync';
export type * from './dashboard';
export type * from './trend';
export type * from './insight';
export type * from './alert';
