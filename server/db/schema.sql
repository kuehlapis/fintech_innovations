-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.agent_outputs (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  analysis_run_id uuid NOT NULL,
  agent_name text,
  output jsonb,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT agent_outputs_pkey PRIMARY KEY (id),
  CONSTRAINT agent_outputs_analysis_run_id_fkey FOREIGN KEY (analysis_run_id) REFERENCES public.analysis_runs(id)
);
CREATE TABLE public.analysis_runs (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  portfolio_id uuid,
  status text DEFAULT 'completed'::text,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT analysis_runs_pkey PRIMARY KEY (id),
  CONSTRAINT analysis_runs_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id),
  CONSTRAINT analysis_runs_portfolio_id_fkey FOREIGN KEY (portfolio_id) REFERENCES public.portfolios(id)
);
CREATE TABLE public.countries (
  code text NOT NULL,
  name text NOT NULL UNIQUE,
  CONSTRAINT countries_pkey PRIMARY KEY (code)
);
CREATE TABLE public.financial_accounts (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  account_type text CHECK (account_type = ANY (ARRAY['bank'::text, 'credit_card'::text])),
  institution_name text,
  account_name text,
  currency text DEFAULT 'USD'::text,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT financial_accounts_pkey PRIMARY KEY (id),
  CONSTRAINT financial_accounts_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.investor_profiles (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL UNIQUE,
  risk_tolerance text CHECK (risk_tolerance = ANY (ARRAY['low'::text, 'medium'::text, 'high'::text])),
  investment_horizon text,
  preferred_sectors ARRAY,
  excluded_sectors ARRAY,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT investor_profiles_pkey PRIMARY KEY (id),
  CONSTRAINT investor_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.portfolio_assets (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  portfolio_id uuid NOT NULL,
  asset_type text CHECK (asset_type = ANY (ARRAY['savings'::text, 'equity'::text, 'bond'::text, 'crypto'::text, 'real_estate'::text, 'private_equity'::text])),
  asset_name text,
  ticker text,
  sector text,
  quantity numeric,
  value numeric,
  country text,
  city text,
  property_type text CHECK (property_type = ANY (ARRAY['residential'::text, 'commercial'::text, 'industrial'::text, 'reit'::text])),
  metadata jsonb,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT portfolio_assets_pkey PRIMARY KEY (id),
  CONSTRAINT portfolio_assets_portfolio_id_fkey FOREIGN KEY (portfolio_id) REFERENCES public.portfolios(id),
  CONSTRAINT portfolio_assets_country_fkey FOREIGN KEY (country) REFERENCES public.countries(code)
);
CREATE TABLE public.portfolio_metrics (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  portfolio_id uuid,
  portfolio_health_score numeric,
  crypto_percentage numeric,
  equity_percentage numeric,
  real_estate_percentage numeric,
  savings_percentage numeric,
  bond_percentage numeric,
  updated_at timestamp without time zone DEFAULT now(),
  CONSTRAINT portfolio_metrics_pkey PRIMARY KEY (id),
  CONSTRAINT portfolio_metrics_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id),
  CONSTRAINT portfolio_metrics_portfolio_id_fkey FOREIGN KEY (portfolio_id) REFERENCES public.portfolios(id)
);
CREATE TABLE public.portfolios (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  portfolio_name text,
  base_currency text DEFAULT 'USD'::text,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT portfolios_pkey PRIMARY KEY (id),
  CONSTRAINT portfolios_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.recommendations (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  analysis_run_id uuid NOT NULL,
  portfolio_health_score numeric,
  risk_level text,
  recommended_allocation jsonb,
  recommendations jsonb,
  reasoning text,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT recommendations_pkey PRIMARY KEY (id),
  CONSTRAINT recommendations_analysis_run_id_fkey FOREIGN KEY (analysis_run_id) REFERENCES public.analysis_runs(id)
);
CREATE TABLE public.statement_uploads (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL,
  account_id uuid,
  file_url text,
  statement_period_start date,
  statement_period_end date,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT statement_uploads_pkey PRIMARY KEY (id),
  CONSTRAINT statement_uploads_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id),
  CONSTRAINT statement_uploads_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.financial_accounts(id)
);
CREATE TABLE public.transactions (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  account_id uuid NOT NULL,
  transaction_date date,
  transaction_type text CHECK (transaction_type = ANY (ARRAY['income'::text, 'expense'::text, 'transfer'::text])),
  category text,
  amount numeric NOT NULL,
  description text,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT transactions_pkey PRIMARY KEY (id),
  CONSTRAINT transactions_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.financial_accounts(id)
);