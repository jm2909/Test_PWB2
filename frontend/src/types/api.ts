export interface ApiErrorBody {
  detail: string;
}

/** Thrown for every non-2xx API response. `detail` is always a displayable string. */
export class ApiError extends Error {
  readonly status: number;
  readonly detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

/** List envelope used by every collection endpoint. */
export interface Page<T> {
  items: T[];
  limit: number;
  offset: number;
  total: number;
}
