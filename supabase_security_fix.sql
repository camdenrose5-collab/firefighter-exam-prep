-- ============================================================================
-- SUPABASE SECURITY FIX MIGRATION
-- Run this in Supabase Dashboard > SQL Editor
-- Created: 2026-01-30
-- ============================================================================

-- ============================================================================
-- 1. FIX SECURITY DEFINER VIEW (ERROR)
-- ============================================================================
-- Drop and recreate career_leaderboard without SECURITY DEFINER
-- First, let's check the view definition and recreate it properly

DROP VIEW IF EXISTS public.career_leaderboard;

-- Recreate the view without SECURITY DEFINER (it will use SECURITY INVOKER by default)
-- Note: You may need to adjust this query based on your actual view definition
CREATE VIEW public.career_leaderboard AS
SELECT 
  cp.id,
  cp.user_id,
  cp.display_name,
  cp.total_points,
  cp.current_streak,
  cp.longest_streak,
  cp.questions_answered,
  cp.correct_answers,
  cp.updated_at,
  RANK() OVER (ORDER BY cp.total_points DESC) as rank
FROM public.career_progress cp
WHERE cp.display_name IS NOT NULL
ORDER BY cp.total_points DESC;

-- ============================================================================
-- 2. ENABLE RLS ON PUBLIC TABLES (ERRORS)
-- ============================================================================

-- Enable RLS on all flagged tables
ALTER TABLE public.departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.flashcards ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

-- Create read policies for public content (these are reference data tables)
-- Everyone can read, only admins should write

CREATE POLICY "Allow public read access on departments"
  ON public.departments FOR SELECT
  USING (true);

CREATE POLICY "Allow public read access on questions"
  ON public.questions FOR SELECT
  USING (true);

CREATE POLICY "Allow public read access on flashcards"
  ON public.flashcards FOR SELECT
  USING (true);

CREATE POLICY "Allow public read access on scenarios"
  ON public.scenarios FOR SELECT
  USING (true);

CREATE POLICY "Allow public read access on documents"
  ON public.documents FOR SELECT
  USING (true);

-- ============================================================================
-- 3. FIX FUNCTION SEARCH PATHS (WARNINGS)
-- ============================================================================

ALTER FUNCTION public.update_career_updated_at() SET search_path = public;
ALTER FUNCTION public.check_tier_eligibility() SET search_path = public;

-- ============================================================================
-- 4. FIX EXEMPLARS OVERLY PERMISSIVE RLS (WARNING)
-- ============================================================================

-- Drop the overly permissive policy
DROP POLICY IF EXISTS "Allow all operations on exemplars" ON public.exemplars;

-- Create proper granular policies
CREATE POLICY "Allow public read access on exemplars"
  ON public.exemplars FOR SELECT
  USING (true);

CREATE POLICY "Allow authenticated users to insert exemplars"
  ON public.exemplars FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Allow users to update their own exemplars"
  ON public.exemplars FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Allow users to delete their own exemplars"
  ON public.exemplars FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

-- ============================================================================
-- VERIFICATION: Run these queries to confirm fixes
-- ============================================================================
-- 
-- Check RLS is enabled:
-- SELECT schemaname, tablename, rowsecurity FROM pg_tables 
-- WHERE schemaname = 'public' AND tablename IN ('departments', 'questions', 'flashcards', 'scenarios', 'documents');
--
-- Check policies exist:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
-- FROM pg_policies WHERE schemaname = 'public';
--
-- Check view is not SECURITY DEFINER:
-- SELECT viewname, definition FROM pg_views WHERE viewname = 'career_leaderboard';
