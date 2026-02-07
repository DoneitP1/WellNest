-- WellNest Database Schema
-- PostgreSQL/SQLite Compatible
-- Version: 2.0 - AI-Powered Health & Calorie Tracking

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_athlete BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster email lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================
-- USER PROFILES TABLE
-- Extended profile with onboarding data
-- ============================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id TEXT PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,

    -- Basic Info
    first_name TEXT,
    last_name TEXT,

    -- Physical Metrics
    height REAL,                          -- cm
    current_weight REAL,                  -- kg
    target_weight REAL,                   -- kg
    birth_date DATE,
    gender TEXT CHECK(gender IN ('male', 'female', 'other')),

    -- Activity & Goals
    activity_level TEXT CHECK(activity_level IN (
        'sedentary',      -- Little to no exercise
        'light',          -- 1-3 days/week
        'moderate',       -- 3-5 days/week
        'active',         -- 6-7 days/week
        'very_active'     -- Professional athlete
    )) DEFAULT 'moderate',

    goal_type TEXT CHECK(goal_type IN (
        'lose_weight',
        'maintain',
        'gain_muscle',
        'improve_health'
    )) DEFAULT 'maintain',

    -- Calculated Goals (updated via triggers/app logic)
    bmr REAL,                             -- Basal Metabolic Rate
    tdee REAL,                            -- Total Daily Energy Expenditure
    daily_calorie_goal INTEGER,
    protein_goal REAL,                    -- grams
    carbs_goal REAL,                      -- grams
    fat_goal REAL,                        -- grams
    daily_water_goal INTEGER DEFAULT 2500, -- ml

    -- Preferences
    preferred_unit TEXT DEFAULT 'metric', -- metric/imperial
    timezone TEXT DEFAULT 'UTC',

    -- Onboarding Status
    onboarding_completed BOOLEAN DEFAULT FALSE,
    onboarding_step INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index for user profile lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);

-- ============================================
-- FOOD LOGS TABLE
-- Enhanced with AI analysis fields
-- ============================================
CREATE TABLE IF NOT EXISTS food_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,

    -- Food Information
    food_name TEXT NOT NULL,
    brand TEXT,                           -- Optional brand name

    -- Nutritional Values
    calories INTEGER NOT NULL,
    protein REAL DEFAULT 0,               -- grams
    carbs REAL DEFAULT 0,                 -- grams
    fat REAL DEFAULT 0,                   -- grams
    fiber REAL DEFAULT 0,                 -- grams
    sugar REAL DEFAULT 0,                 -- grams
    sodium REAL DEFAULT 0,                -- mg

    -- Serving Information
    serving_size REAL DEFAULT 1,
    serving_unit TEXT DEFAULT 'portion',  -- g, ml, cup, piece, portion

    -- Meal Classification
    meal_type TEXT CHECK(meal_type IN (
        'breakfast',
        'lunch',
        'dinner',
        'snack',
        'pre_workout',
        'post_workout'
    )) DEFAULT 'snack',

    -- AI Analysis Fields
    image_url TEXT,                       -- Stored image URL/path
    ai_analyzed BOOLEAN DEFAULT FALSE,
    ai_confidence_score REAL,             -- 0.0 to 1.0
    ai_raw_response TEXT,                 -- JSON string of full AI response
    user_confirmed BOOLEAN DEFAULT TRUE,  -- User confirmed AI suggestion

    -- Timestamps
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for food logs
CREATE INDEX IF NOT EXISTS idx_food_logs_user_id ON food_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_food_logs_logged_at ON food_logs(logged_at);
CREATE INDEX IF NOT EXISTS idx_food_logs_user_date ON food_logs(user_id, logged_at);

-- ============================================
-- WEIGHT LOGS TABLE
-- Enhanced with body composition
-- ============================================
CREATE TABLE IF NOT EXISTS weight_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,

    -- Weight Data
    weight REAL NOT NULL,                 -- kg

    -- Optional Body Composition (for smart scales)
    body_fat_percentage REAL,
    muscle_mass REAL,                     -- kg
    bone_mass REAL,                       -- kg
    water_percentage REAL,
    visceral_fat INTEGER,                 -- Level 1-59
    metabolic_age INTEGER,

    -- Source
    source TEXT DEFAULT 'manual',         -- manual, healthkit, googlefit, smart_scale

    -- Timestamps
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for weight logs
CREATE INDEX IF NOT EXISTS idx_weight_logs_user_id ON weight_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_weight_logs_logged_at ON weight_logs(logged_at);

-- ============================================
-- WATER LOGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS water_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,

    amount_ml INTEGER NOT NULL,

    -- Timestamps
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for water logs
CREATE INDEX IF NOT EXISTS idx_water_logs_user_id ON water_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_water_logs_logged_at ON water_logs(logged_at);

-- ============================================
-- DAILY STATS TABLE
-- Aggregated daily statistics
-- ============================================
CREATE TABLE IF NOT EXISTS daily_stats (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,

    -- Nutrition Summary
    total_calories INTEGER DEFAULT 0,
    total_protein REAL DEFAULT 0,
    total_carbs REAL DEFAULT 0,
    total_fat REAL DEFAULT 0,
    total_fiber REAL DEFAULT 0,
    total_water_ml INTEGER DEFAULT 0,

    -- Activity Data (from integrations)
    steps INTEGER DEFAULT 0,
    distance_km REAL DEFAULT 0,
    active_calories INTEGER DEFAULT 0,
    exercise_minutes INTEGER DEFAULT 0,

    -- Health Metrics (from integrations)
    sleep_hours REAL,
    sleep_quality_score INTEGER,          -- 0-100
    avg_heart_rate INTEGER,
    resting_heart_rate INTEGER,
    hrv_ms INTEGER,                       -- Heart Rate Variability in ms

    -- Calculated Scores
    recovery_score INTEGER,               -- 0-100 (for athletes)
    calorie_balance INTEGER,              -- calories in - calories out
    goal_adherence_score INTEGER,         -- 0-100

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, date)
);

-- Indexes for daily stats
CREATE INDEX IF NOT EXISTS idx_daily_stats_user_id ON daily_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date);
CREATE INDEX IF NOT EXISTS idx_daily_stats_user_date ON daily_stats(user_id, date);

-- ============================================
-- ATHLETE METRICS TABLE
-- Professional athlete specific tracking
-- ============================================
CREATE TABLE IF NOT EXISTS athlete_metrics (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,

    -- Training Metrics
    training_load INTEGER,                -- RPE * duration (arbitrary units)
    training_type TEXT,                   -- strength, cardio, hiit, sport_specific
    training_duration_min INTEGER,
    rpe_score INTEGER CHECK(rpe_score BETWEEN 1 AND 10), -- Rate of Perceived Exertion

    -- Performance Metrics
    vo2_max_estimate REAL,
    lactate_threshold_hr INTEGER,
    power_output_watts REAL,              -- For cycling/rowing
    pace_per_km TEXT,                     -- For running (mm:ss format)

    -- Recovery Metrics
    hrv_score REAL,
    resting_hr INTEGER,
    sleep_hours REAL,
    sleep_quality INTEGER,                -- 0-100
    muscle_soreness INTEGER CHECK(muscle_soreness BETWEEN 1 AND 10),
    fatigue_level INTEGER CHECK(fatigue_level BETWEEN 1 AND 10),
    stress_level INTEGER CHECK(stress_level BETWEEN 1 AND 10),

    -- Calculated Scores
    readiness_score INTEGER,              -- 0-100, overall readiness to train
    acute_load REAL,                      -- 7-day rolling average
    chronic_load REAL,                    -- 28-day rolling average
    acwr REAL,                            -- Acute:Chronic Workload Ratio

    -- Notes
    notes TEXT,
    injury_notes TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, date)
);

-- Indexes for athlete metrics
CREATE INDEX IF NOT EXISTS idx_athlete_metrics_user_id ON athlete_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_athlete_metrics_date ON athlete_metrics(date);

-- ============================================
-- HEALTH INTEGRATIONS TABLE
-- Track connected health platforms
-- ============================================
CREATE TABLE IF NOT EXISTS health_integrations (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,

    -- Integration Info
    platform TEXT NOT NULL CHECK(platform IN (
        'apple_healthkit',
        'google_fit',
        'fitbit',
        'garmin',
        'whoop',
        'oura'
    )),

    -- Connection Status
    is_connected BOOLEAN DEFAULT FALSE,
    access_token TEXT,                    -- Encrypted
    refresh_token TEXT,                   -- Encrypted
    token_expires_at TIMESTAMP,

    -- Sync Settings
    sync_enabled BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMP,
    sync_frequency_minutes INTEGER DEFAULT 60,

    -- Data Permissions
    sync_steps BOOLEAN DEFAULT TRUE,
    sync_weight BOOLEAN DEFAULT TRUE,
    sync_sleep BOOLEAN DEFAULT TRUE,
    sync_heart_rate BOOLEAN DEFAULT TRUE,
    sync_workouts BOOLEAN DEFAULT TRUE,
    sync_nutrition BOOLEAN DEFAULT FALSE, -- Usually we write, not read

    -- Timestamps
    connected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, platform)
);

-- Index for health integrations
CREATE INDEX IF NOT EXISTS idx_health_integrations_user_id ON health_integrations(user_id);

-- ============================================
-- FOOD DATABASE TABLE
-- Common foods for quick lookup & offline
-- ============================================
CREATE TABLE IF NOT EXISTS food_database (
    id TEXT PRIMARY KEY,

    -- Food Information
    name TEXT NOT NULL,
    name_tr TEXT,                         -- Turkish name
    brand TEXT,
    category TEXT,                        -- vegetables, fruits, protein, dairy, grains, etc.

    -- Nutritional Values (per 100g or standard serving)
    calories INTEGER NOT NULL,
    protein REAL DEFAULT 0,
    carbs REAL DEFAULT 0,
    fat REAL DEFAULT 0,
    fiber REAL DEFAULT 0,
    sugar REAL DEFAULT 0,
    sodium REAL DEFAULT 0,

    -- Serving Info
    standard_serving_size REAL,
    standard_serving_unit TEXT,

    -- Metadata
    barcode TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    popularity_score INTEGER DEFAULT 0,   -- For search ranking

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for food database
CREATE INDEX IF NOT EXISTS idx_food_database_name ON food_database(name);
CREATE INDEX IF NOT EXISTS idx_food_database_barcode ON food_database(barcode);
CREATE INDEX IF NOT EXISTS idx_food_database_category ON food_database(category);

-- ============================================
-- USER FAVORITES TABLE
-- Quick access to frequently logged foods
-- ============================================
CREATE TABLE IF NOT EXISTS user_favorites (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    food_database_id TEXT,                -- Reference to food_database

    -- Or custom food data
    custom_food_name TEXT,
    custom_calories INTEGER,
    custom_protein REAL,
    custom_carbs REAL,
    custom_fat REAL,

    -- Usage tracking
    use_count INTEGER DEFAULT 1,
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (food_database_id) REFERENCES food_database(id) ON DELETE SET NULL
);

-- Index for user favorites
CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id ON user_favorites(user_id);

-- ============================================
-- GOALS TABLE
-- Custom user goals beyond defaults
-- ============================================
CREATE TABLE IF NOT EXISTS user_goals (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,

    -- Goal Definition
    goal_type TEXT NOT NULL,              -- weight, steps, water, protein, etc.
    target_value REAL NOT NULL,
    current_value REAL DEFAULT 0,
    unit TEXT,                            -- kg, steps, ml, g, etc.

    -- Timeline
    start_date DATE NOT NULL,
    target_date DATE,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_achieved BOOLEAN DEFAULT FALSE,
    achieved_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index for user goals
CREATE INDEX IF NOT EXISTS idx_user_goals_user_id ON user_goals(user_id);

-- ============================================
-- SYNC QUEUE TABLE
-- Offline-first: queue for pending syncs
-- ============================================
CREATE TABLE IF NOT EXISTS sync_queue (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,

    -- Sync Data
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    operation TEXT CHECK(operation IN ('INSERT', 'UPDATE', 'DELETE')),
    data_json TEXT,                       -- JSON of the record

    -- Status
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'syncing', 'synced', 'failed')),
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synced_at TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index for sync queue
CREATE INDEX IF NOT EXISTS idx_sync_queue_status ON sync_queue(status);
CREATE INDEX IF NOT EXISTS idx_sync_queue_user_id ON sync_queue(user_id);

-- ============================================
-- VIEWS
-- ============================================

-- Daily Summary View
CREATE VIEW IF NOT EXISTS v_daily_summary AS
SELECT
    u.id as user_id,
    u.email,
    DATE(fl.logged_at) as date,
    SUM(fl.calories) as total_calories,
    SUM(fl.protein) as total_protein,
    SUM(fl.carbs) as total_carbs,
    SUM(fl.fat) as total_fat,
    COUNT(fl.id) as meal_count,
    up.daily_calorie_goal,
    up.daily_calorie_goal - SUM(fl.calories) as remaining_calories
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
LEFT JOIN food_logs fl ON u.id = fl.user_id
GROUP BY u.id, DATE(fl.logged_at);

-- Weekly Progress View
CREATE VIEW IF NOT EXISTS v_weekly_progress AS
SELECT
    user_id,
    strftime('%Y-%W', logged_at) as year_week,
    AVG(weight) as avg_weight,
    MIN(weight) as min_weight,
    MAX(weight) as max_weight,
    COUNT(*) as log_count
FROM weight_logs
GROUP BY user_id, strftime('%Y-%W', logged_at);
