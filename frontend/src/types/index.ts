export { ApiError } from './api';
export type { ApiErrorBody, Page } from './api';
export type { Account, TokenResponse, LoginRequest } from './auth';
export type { RegisterRequest } from './auth';
export type { ConsentDecision, ConsentRecord, ConsentRequest, DataCategory } from './consent';
export type { DataRightsRequest, DataRightsRequestCreate, DataRightsType } from './dataRights';
export type {
  ConnectionItem,
  ConnectionResult,
  ConnectionStatus,
  RecoveryAction,
  ScaleConnectRequest,
  WearableAuthorization,
  WearableCallback,
  WearableProvider,
} from './connection';
export type { TrendMetric, TrendPoint, TrendRange, TrendResponse } from './trend';
export type { Insight, InsightFeedback } from './insight';
export type { AlertState, WellnessAlert } from './alert';
export type {
  DashboardAlert,
  DashboardData,
  DashboardGoal,
  DashboardInsightItem,
  DashboardMeasurement,
  DashboardSourceStatus,
  UnavailableCategory,
} from './dashboard';
export type {
  SupportCategory,
  SupportContextType,
  SupportRequestCreate,
  SupportRequestReceipt,
} from './support';
export type { Goal, GoalCategory, GoalCreateRequest, GoalMetric, GoalState } from './goal';
