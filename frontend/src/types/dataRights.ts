export type DataRightsType = 'export' | 'deletion';

export interface DataRightsRequestCreate {
  request_type: DataRightsType;
  description?: string;
}

export interface DataRightsRequest {
  id: string;
  reference: string;
  request_type: DataRightsType;
  status: string;
  requested_at: string;
  fulfillment_due_at: string;
}
