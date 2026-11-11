export type SupportCategory = 'connection' | 'data_quality' | 'account' | 'alert';
export type SupportContextType = 'device' | 'account' | 'alert';

export interface SupportRequestCreate {
  category: SupportCategory;
  description: string;
  context_type: SupportContextType;
  context_id?: string;
}

export interface SupportRequestReceipt {
  id: string;
  reference: string;
  status: string;
  submitted_at: string;
}
