
-- ============================================================
-- Enable UUID extension
-- ============================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- USERS & PORTFOLIOS
-- ============================================================

-- Portfolio table (one portfolio per user)
CREATE TABLE IF NOT EXISTS public.portfolios (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    user_id uuid UNIQUE NOT NULL REFERENCES auth.users(id),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    PRIMARY KEY (id)
);

-- ============================================================
-- ASSETS
-- ============================================================

CREATE TABLE IF NOT EXISTS public.assets (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    ticker text,
    asset_class text NOT NULL,
    created_at timestamptz DEFAULT now(),
    PRIMARY KEY (id)
);

-- ============================================================
-- PORTFOLIO ASSETS
-- ============================================================

CREATE TABLE IF NOT EXISTS public.portfolio_assets (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    portfolio_id uuid NOT NULL REFERENCES public.portfolios(id) ON DELETE CASCADE,
    asset_id uuid NOT NULL REFERENCES public.assets(id) ON DELETE CASCADE,
    quantity double precision NOT NULL CHECK (quantity > 0),
    entry_price double precision,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    PRIMARY KEY (id)
);

-- ============================================================
-- PROPERTY ASSETS
-- ============================================================

CREATE TABLE IF NOT EXISTS public.property_assets (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    asset_id uuid NOT NULL REFERENCES public.assets(id) ON DELETE CASCADE,
    address text,
    purchase_price double precision,
    mortgage_value double precision,
    interest_rate double precision,
    rental_income double precision,
    remaining_lease text,
    other_details jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    PRIMARY KEY (id)
);

-- ============================================================
-- ASSET PRICES
-- ============================================================

CREATE TABLE IF NOT EXISTS public.asset_prices (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    asset_id uuid NOT NULL REFERENCES public.assets(id) ON DELETE CASCADE,
    price double precision NOT NULL,
    source text,
    timestamp timestamptz DEFAULT now(),
    PRIMARY KEY (id)
);

-- ============================================================
-- PORTFOLIO HEALTH
-- ============================================================

CREATE TABLE IF NOT EXISTS public.portfolio_health (
    portfolio_id uuid NOT NULL REFERENCES public.portfolios(id) ON DELETE CASCADE,
    total_value double precision,
    diversification_score double precision CHECK (diversification_score >= 0 AND diversification_score <= 1),
    liquidity_ratio double precision,
    sentiment_score double precision CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    wellness_score integer CHECK (wellness_score >= 0 AND wellness_score <= 100),
    advisory_text text,
    asset_weights jsonb,
    price_snapshot jsonb,
    updated_at timestamptz DEFAULT now(),
    PRIMARY KEY (portfolio_id)
);

-- ============================================================
-- PORTFOLIO HISTORY
-- ============================================================

CREATE TABLE IF NOT EXISTS public.portfolio_history (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    portfolio_id uuid NOT NULL REFERENCES public.portfolios(id) ON DELETE CASCADE,
    total_value double precision,
    created_at timestamptz DEFAULT now(),
    PRIMARY KEY (id)
);

-- ============================================================
-- AI INSIGHTS
-- ============================================================

CREATE TABLE IF NOT EXISTS public.ai_insights (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    portfolio_id uuid NOT NULL REFERENCES public.portfolios(id) ON DELETE CASCADE,
    agent_name text,
    recommendation text,
    confidence_score double precision,
    created_at timestamptz DEFAULT now(),
    PRIMARY KEY (id)
);

-- ============================================================
-- TRANSACTIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS public.transactions (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    portfolio_id uuid NOT NULL REFERENCES public.portfolios(id) ON DELETE CASCADE,
    asset_id uuid NOT NULL REFERENCES public.assets(id) ON DELETE CASCADE,
    transaction_type text CHECK (transaction_type IN ('buy','sell')),
    quantity double precision NOT NULL,
    price double precision NOT NULL,
    created_at timestamptz DEFAULT now(),
    PRIMARY KEY (id)
);

-- ============================================================
-- ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================================

ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolio_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.property_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.asset_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolio_health ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolio_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- RLS POLICIES
-- ============================================================

-- Users can access their own portfolio
CREATE POLICY "Users can manage their portfolio"
    ON public.portfolios
    FOR ALL
    USING (user_id = auth.uid());

-- Users can manage assets in their own portfolio
CREATE POLICY "Users can manage portfolio_assets"
    ON public.portfolio_assets
    FOR ALL
    USING (portfolio_id IN (SELECT id FROM public.portfolios WHERE user_id = auth.uid()));

-- Users can manage property assets linked to their portfolio
CREATE POLICY "Users can manage property_assets"
    ON public.property_assets
    FOR ALL
    USING (asset_id IN (SELECT asset_id FROM public.portfolio_assets WHERE portfolio_id IN (SELECT id FROM public.portfolios WHERE user_id = auth.uid())));

-- Users can read asset prices (optional: allow read-only for all users)
CREATE POLICY "Users can read asset_prices"
    ON public.asset_prices
    FOR SELECT
    USING (TRUE);

-- Users can manage their portfolio health
ALTER TABLE public.portfolio_health ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only read their own portfolio_health
CREATE POLICY "Users can read portfolio_health"
    ON public.portfolio_health
    FOR SELECT
    USING (
        portfolio_id IN (
            SELECT id 
            FROM public.portfolios 
            WHERE user_id = auth.uid()
        )
    );

-- Users can manage portfolio history
ALTER TABLE public.portfolio_history ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only read their own portfolio history
CREATE POLICY "Users can read portfolio_history"
    ON public.portfolio_history
    FOR SELECT
    USING (
        portfolio_id IN (
            SELECT id
            FROM public.portfolios
            WHERE user_id = auth.uid()
        )
    );

-- Users can manage AI insights for their portfolio

ALTER TABLE public.ai_insights ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage ai_insights"
    ON public.ai_insights
    FOR SELECT
    USING (portfolio_id IN (SELECT id FROM public.portfolios WHERE user_id = auth.uid()));

-- Users can manage their transactions
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only read their own transactions
CREATE POLICY "Users can read transactions"
    ON public.transactions
    FOR SELECT
    USING (
        portfolio_id IN (
            SELECT id
            FROM public.portfolios
            WHERE user_id = auth.uid()
        )
    );

-- Enable RLS on assets
ALTER TABLE public.assets ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read assets linked to their portfolio
CREATE POLICY "Users can read their assets"
    ON public.assets
    FOR SELECT
    USING (
        id IN (
            SELECT asset_id 
            FROM public.portfolio_assets 
            WHERE portfolio_id IN (
                SELECT id 
                FROM public.portfolios 
                WHERE user_id = auth.uid()
            )
        )
    );

-- Policy: Users can insert assets if they are linked to their portfolio
CREATE POLICY "Users can insert assets"
    ON public.assets
    FOR INSERT
    WITH CHECK (
        id IN (
            SELECT asset_id 
            FROM public.portfolio_assets 
            WHERE portfolio_id IN (
                SELECT id 
                FROM public.portfolios 
                WHERE user_id = auth.uid()
            )
        )
    );

-- Policy: Users can update assets linked to their portfolio
CREATE POLICY "Users can update assets"
    ON public.assets
    FOR UPDATE
    USING (
        id IN (
            SELECT asset_id 
            FROM public.portfolio_assets 
            WHERE portfolio_id IN (
                SELECT id 
                FROM public.portfolios 
                WHERE user_id = auth.uid()
            )
        )
    );

-- Policy: Users can delete assets linked to their portfolio
CREATE POLICY "Users can delete assets"
    ON public.assets
    FOR DELETE
    USING (
        id IN (
            SELECT asset_id 
            FROM public.portfolio_assets 
            WHERE portfolio_id IN (
                SELECT id 
                FROM public.portfolios 
                WHERE user_id = auth.uid()
            )
        )
    );