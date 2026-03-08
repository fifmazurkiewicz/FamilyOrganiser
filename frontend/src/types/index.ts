// ──────────────────────────────────────────────
// Core domain types mirroring backend schemas
// ──────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  full_name: string;
  default_currency: string;
  avatar_url?: string;
  is_app_admin: boolean;
  is_locked: boolean;
  created_at: string;
}

export interface FamilyGroup {
  id: string;
  name: string;
  description?: string;
  owner_id: string;
  member_count: number;
  created_at: string;
}

export interface FamilyMembership {
  user_id: string;
  group_id: string;
  role: "admin" | "member";
  share_expenses: boolean;
  share_savings: boolean;
  share_investments: boolean;
  joined_at: string;
}

export interface Account {
  id: string;
  owner_id: string;
  name: string;
  account_type: AccountType;
  balance: number;
  currency: string;
  bank_name?: string;
  iban?: string;
  credit_limit?: number;
  interest_rate?: number;
  is_active: boolean;
  created_at: string;
}

export type AccountType =
  | "checking"
  | "savings"
  | "credit_card"
  | "investment"
  | "cash"
  | "mortgage"
  | "other";

export interface Transaction {
  id: string;
  user_id: string;
  account_id: string;
  category_id?: string;
  amount: number;
  amount_pln: number;
  currency: string;
  description?: string;
  merchant?: string;
  transaction_date: string;
  transaction_type: "expense" | "income" | "transfer";
  tags: string[];
  created_at: string;
}

export interface TransactionCategory {
  id: string;
  name: string;
  icon?: string;
  color?: string;
  parent_id?: string;
  is_system: boolean;
}

export interface Budget {
  id: string;
  user_id: string;
  name: string;
  scope: "personal" | "family";
  year: number;
  month?: number;
  alert_threshold_percent: number;
  categories: BudgetCategory[];
  created_at: string;
}

export interface BudgetCategory {
  id: string;
  category_id: string;
  planned_amount: number;
  currency: string;
  actual_amount: number;
}

export interface SavingsGoal {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  icon?: string;
  color?: string;
  target_amount: number;
  current_amount: number;
  currency: string;
  goal_type: "personal" | "family";
  visibility: "private" | "group" | "public";
  target_date?: string;
  monthly_contribution?: number;
  is_completed: boolean;
  is_active: boolean;
  priority: number;
  progress_percent: number;
  created_at: string;
}

export interface SavingsContribution {
  id: string;
  goal_id: string;
  user_id: string;
  amount: number;
  currency: string;
  contribution_date: string;
  note?: string;
  is_withdrawal: boolean;
  created_at: string;
}

export interface Investment {
  id: string;
  user_id: string;
  investment_type: InvestmentType;
  name: string;
  ticker?: string;
  quantity?: number;
  purchase_price?: number;
  current_price?: number;
  currency: string;
  purchase_date?: string;
  notes?: string;
  is_shared: boolean;
  total_value?: number;
  roi_percent?: number;
  created_at: string;
}

export type InvestmentType =
  | "stock"
  | "etf"
  | "fund"
  | "real_estate"
  | "crypto"
  | "polish_bond"
  | "bank_deposit";

export interface PolishBond {
  id: string;
  bond_type: string;
  series: string;
  quantity: number;
  purchase_date: string;
  maturity_date: string;
  first_period_rate: number;
  current_value: number;
  nominal_value: number;
  accrued_interest: number;
  is_active: boolean;
  notes?: string;
}

export interface IncomeTemplate {
  id: string;
  account_id: string;
  name: string;
  base_amount: number;
  currency: string;
  category: IncomeCategory;
  day_of_month: number;
  is_active: boolean;
}

export type IncomeCategory =
  | "salary"
  | "freelance"
  | "rental"
  | "dividend"
  | "interest"
  | "bonus"
  | "pension"
  | "other";

export interface Income {
  id: string;
  user_id: string;
  account_id: string;
  template_id?: string;
  name: string;
  amount: number;
  base_amount?: number;
  currency: string;
  category: IncomeCategory;
  income_date: string;
  is_modified: boolean;
  is_skipped: boolean;
  description?: string;
  created_at: string;
}

export interface Transfer {
  id: string;
  transfer_type: TransferType;
  from_account_id?: string;
  to_account_id?: string;
  from_goal_id?: string;
  to_goal_id?: string;
  amount: number;
  currency: string;
  transfer_date: string;
  description?: string;
}

export type TransferType =
  | "account_to_account"
  | "account_to_goal"
  | "goal_to_account"
  | "goal_to_goal";

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  data?: Record<string, unknown>;
  created_at: string;
}

export interface ExchangeRate {
  currency: string;
  rate_to_pln: number;
  date: string;
}

// ── Dashboard / reports ──

export interface DashboardData {
  total_assets: number;
  total_liabilities: number;
  net_worth: number;
  monthly_income: number;
  monthly_expenses: number;
  savings_rate: number;
  top_expenses: { category: string; amount: number }[];
  active_goals: SavingsGoal[];
  recent_transactions: Transaction[];
}

export interface MonthlyTrend {
  month: string;
  income: number;
  expenses: number;
  savings: number;
}

// ── Auth ──

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  security_question: string;
  security_answer: string;
}
