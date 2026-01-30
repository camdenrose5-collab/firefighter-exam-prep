-- ============================================================================
-- SUPABASE SECURITY FIX MIGRATION
-- Run in Supabase Dashboard > SQL Editor
-- Created: 2026-01-30 | Applied: 2026-01-30
-- ============================================================================

-- 1. FIX SECURITY DEFINER VIEW
DROP VIEW IF EXISTS public.career_leaderboard;
CREATE VIEW public.career_leaderboard AS
SELECT id,
    user_id,
    department_id,
    display_name,
    tier,
    total_command_hours,
    scenario_count,
    average_score,
    pass_rate,
    ( SELECT count(*) AS count
           FROM competency_badges cb
          WHERE ((cb.user_id = cp.user_id) AND (cb.department_id = cp.department_id))) AS badge_count,
    rank() OVER (PARTITION BY department_id ORDER BY average_score DESC NULLS LAST) AS department_rank
   FROM career_profiles cp;

-- 2. ENABLE RLS ON PUBLIC TABLES
ALTER TABLE public.departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.flashcards ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

-- 3. READ POLICIES
CREATE POLICY "Allow public read access on departments" ON public.departments FOR SELECT USING (true);
CREATE POLICY "Allow public read access on questions" ON public.questions FOR SELECT USING (true);
CREATE POLICY "Allow public read access on flashcards" ON public.flashcards FOR SELECT USING (true);
CREATE POLICY "Allow public read access on scenarios" ON public.scenarios FOR SELECT USING (true);
CREATE POLICY "Allow public read access on documents" ON public.documents FOR SELECT USING (true);

-- 4. FIX FUNCTION SEARCH PATH
DO $$ BEGIN
  ALTER FUNCTION public.update_career_updated_at() SET search_path = public;
EXCEPTION WHEN undefined_function THEN NULL;
END $$;

-- 5. FIX EXEMPLARS OVERLY PERMISSIVE RLS
DROP POLICY IF EXISTS "Allow all operations on exemplars" ON public.exemplars;
CREATE POLICY "Allow public read access on exemplars" ON public.exemplars FOR SELECT USING (true);
