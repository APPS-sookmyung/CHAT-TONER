# Sub-Agent Tech Debt Finder & Fixer Command

A two-phase command that first identifies technical debt across your codebase, presents findings for review, then orchestrates specialized sub-agents to systematically fix the issues while ensuring code stability.

## Command Syntax

```bash
sub-agent-tech-debt-finder-fixer [target] [options]

# Aliases
@tech-debt-finder-fixer [target] [options]
@td-finder-fixer [target] [options]
@satdff [target] [options]
```

## Parameters

### Target
- `target` - Directory, file, or glob pattern to analyze (defaults to current directory)

### Options
- `--type` - Types of tech debt to find (duplicates, complexity, patterns, dead-code, types, all)
- `--threshold` - Sensitivity threshold (aggressive, standard, conservative)
- `--auto-fix` - Auto-fix level (none, safe, recommended, all)
- `--interactive` - Review each fix before applying (default: true)
- `--dry-run` - Show what would be fixed without making changes
- `--fix-order` - Order of fixes (risk, impact, quick-wins, custom)
- `--backup` - Create backups before fixes (default: true)
- `--test-command` - Command to run tests between fixes
- `--max-changes` - Maximum number of fixes per run
- `--ignore` - Patterns to ignore (.techdebtignore file)

## Examples

### Basic Usage
```bash
# Find and fix tech debt with review
sub-agent-tech-debt-finder-fixer

# Quick wins only - safe fixes
sub-agent-tech-debt-finder-fixer --auto-fix safe --fix-order quick-wins

# Dry run to see what would be fixed
sub-agent-tech-debt-finder-fixer --dry-run
```

### Advanced Usage
```bash
# Focus on duplicate code with aggressive detection
sub-agent-tech-debt-finder-fixer src/ \
  --type duplicates \
  --threshold aggressive \
  --auto-fix recommended

# Full scan with custom test command
sub-agent-tech-debt-finder-fixer \
  --auto-fix safe \
  --test-command "npm test && npm run lint" \
  --max-changes 10

# Non-interactive mode for CI/CD
sub-agent-tech-debt-finder-fixer \
  --interactive false \
  --auto-fix safe \
  --fix-order risk
```

## Phase 1: Finding Tech Debt (Parallel Agents)

### Agent 1: Duplicate Code Detector
```
Find duplicate code in [TARGET]

Detection Tasks:
1. Exact Duplicates:
   - Copy-pasted code blocks
   - Identical functions in different files
   - Repeated constants/configurations
   - Duplicate type definitions
   - Identical test patterns

2. Similar Code (70%+ similarity):
   - Functions with minor parameter differences
   - Components with slight prop variations
   - Similar error handling patterns
   - Repeated validation logic
   - Near-identical API calls

3. Pattern Duplicates:
   - Repeated design patterns
   - Similar file structures
   - Duplicate business logic
   - Repeated UI patterns
   - Similar data transformations

4. Should-Be-Utils:
   - Date formatting functions
   - String manipulation
   - Array operations
   - API request builders
   - Validation helpers

Return:
- Duplicate groups with file:line references
- Similarity percentages
- Suggested utility locations
- Extraction difficulty rating
- Potential names for utilities
```

### Agent 2: Complexity & Size Analyzer
```
Analyze code complexity and file sizes in [TARGET]

Complexity Detection:
1. File Size Violations:
   - Files over 300 lines
   - Components over 200 lines
   - Classes with 10+ methods
   - Modules with 5+ exports
   - Test files over 500 lines

2. Function Complexity:
   - Functions over 30 lines
   - Cyclomatic complexity > 10
   - Cognitive complexity > 15
   - Deep nesting (>4 levels)
   - Too many parameters (>4)

3. Component Complexity:
   - God components doing too much
   - Prop drilling depth > 3
   - Too many state variables
   - Mixed concerns (UI + logic)
   - Render method > 50 lines

4. Architectural Complexity:
   - Circular dependencies
   - Too many imports (>15)
   - Deep inheritance chains
   - Tight coupling
   - Missing abstractions

Return:
- Complexity hotspots with metrics
- Suggested split points
- Refactoring strategies
- Component extraction opportunities
- Architecture improvements
```

### Agent 3: Pattern Inconsistency Detector
```
Find inconsistent patterns in [TARGET]

Pattern Analysis:
1. Naming Inconsistencies:
   - Mixed camelCase/snake_case
   - Inconsistent prefixes (handle/on)
   - Variable naming patterns
   - File naming conventions
   - Component naming standards

2. Code Style Variations:
   - Mixed async patterns (callbacks/promises/async)
   - Inconsistent error handling
   - Different import styles
   - Mixed class/functional components
   - Varying export patterns

3. Framework Usage:
   - Old syntax still in use
   - Mixed state management
   - Inconsistent hook usage
   - Different routing patterns
   - Varying API call methods

4. Project Structure:
   - Inconsistent folder organization
   - Mixed file locations
   - Varying module boundaries
   - Different test locations
   - Inconsistent config files

Return:
- Pattern violations by category
- Most common pattern for each
- Migration effort estimates
- Auto-fixable vs manual
- Impact on codebase consistency
```

### Agent 4: Dead Code Detector
```
Find unused code in [TARGET]

Dead Code Detection:
1. Unused Exports:
   - Functions never imported
   - Components never used
   - Constants never referenced
   - Types never used
   - Classes never instantiated

2. Unreachable Code:
   - Code after return statements
   - Impossible conditions
   - Never-true if blocks
   - Unused switch cases
   - Dead exception handlers

3. Unused Dependencies:
   - npm packages never imported
   - Imported but unused modules
   - Dev dependencies in production
   - Duplicate package functionality
   - Version mismatches

4. Obsolete Code:
   - Commented-out code blocks
   - TODO comments > 6 months
   - Deprecated API usage
   - Legacy compatibility code
   - Feature flags never removed

Return:
- Dead code locations
- Safe to remove vs needs review
- Dependency cleanup list
- Impact on bundle size
- Historical context (git blame)
```

### Agent 5: Type Coverage Analyzer
```
Analyze TypeScript type coverage in [TARGET]

Type Analysis:
1. Missing Types:
   - Implicit any usage
   - Missing return types
   - Untyped function parameters
   - Missing interface definitions
   - Any in generics

2. Weak Types:
   - Overuse of any/unknown
   - String literals instead of enums
   - Missing discriminated unions
   - Weak object types
   - No strict null checks

3. Type Duplication:
   - Repeated interface definitions
   - Similar type structures
   - Inline types that should be extracted
   - Inconsistent type patterns
   - Missing type utilities

4. Type Safety Gaps:
   - Type assertions without guards
   - Missing runtime validation
   - API response types
   - Event handler types
   - Third-party library types

Return:
- Type coverage percentage
- Any usage locations
- Type improvement priorities
- Suggested type definitions
- Type safety score
```

## Synthesis & Presentation Agent

```
Synthesize findings from all detection agents: [ALL_FINDINGS]
Create tech debt report and fix recommendations.

Tasks:
1. Categorize Findings:
   - Group by type and severity
   - Identify related issues
   - Find root causes
   - Calculate total debt score

2. Prioritize Fixes:
   - Quick wins (< 30 min)
   - High impact improvements
   - Risk-based ordering
   - Dependency ordering
   - Team capacity matching

3. Create Fix Plan:
   - Batch related fixes
   - Order by dependencies
   - Estimate time/effort
   - Identify blockers
   - Plan verification steps

4. Risk Assessment:
   - Breaking change potential
   - Test coverage gaps
   - Performance impacts
   - User-facing changes
   - Integration risks

Generate:
- Executive summary
- Detailed findings report
- Prioritized fix list
- Implementation roadmap
- Metrics and scores
```

### Example Report Output
```
🔍 Tech Debt Analysis Complete
==============================

📊 Summary
- Total Issues Found: 127
- Estimated Cleanup Time: 34 hours
- Potential Bundle Reduction: 23%
- Type Coverage Improvement: +18%

🎯 Quick Wins (2 hours total)
1. Remove 15 unused imports → -5KB bundle
2. Delete 8 commented code blocks → -500 lines
3. Extract 5 date utilities → -200 lines duplication

⚡ High Impact (8 hours total)
1. Split UserDashboard.tsx (450 lines) → 3 components
2. Consolidate 12 API call patterns → 1 service
3. Fix 23 any types → +8% type coverage

🔧 Recommended Fix Order:
1. [SAFE] Remove dead code
2. [SAFE] Extract duplicate utilities
3. [MEDIUM] Split large files
4. [MEDIUM] Standardize patterns
5. [REVIEW] Refactor complex logic

Proceed with fixes? [Y/n]:
```

## Phase 2: Fixing Tech Debt

### Pre-Flight Check Agent
```
Verify system ready for fixes:
1. Git status is clean
2. All tests passing
3. Build succeeds
4. No uncommitted changes
5. Backup branch created

Return: Go/No-go decision
```

### Fix Orchestrator Agent
```
Coordinate fix implementation based on user approval: [APPROVED_FIXES]

Orchestration Tasks:
1. Order fixes by dependency
2. Group related fixes
3. Assign to specialized agents
4. Monitor progress
5. Verify each fix
6. Rollback if needed

For each fix:
- Create atomic commit
- Run tests
- Verify behavior unchanged
- Update progress
```

### Specialized Fix Agents (Parallel)

#### Agent F1: Utility Extractor
```
Extract utilities from duplicated code: [DUPLICATES_TO_FIX]

Tasks:
1. Create utility files:
   - Choose appropriate location
   - Follow naming conventions
   - Add comprehensive types
   - Include JSDoc comments

2. Extract common code:
   - Parameterize differences
   - Handle edge cases
   - Maintain behavior
   - Add unit tests

3. Update references:
   - Replace all usages
   - Update imports
   - Fix relative paths
   - Remove old code

Requirements:
- No behavior changes
- All tests must pass
- Follow project patterns
```

#### Agent F2: File Splitter
```
Split large files: [FILES_TO_SPLIT]

Tasks:
1. Analyze file structure:
   - Identify logical boundaries
   - Find extraction points
   - Plan new file structure
   - Consider imports

2. Extract components:
   - Move related code together
   - Maintain interfaces
   - Update imports/exports
   - Preserve functionality

3. Organize results:
   - Create logical folders
   - Update index files
   - Fix all references
   - Clean up old file

Requirements:
- Maintain all functionality
- Keep same public API
- Update all imports
```

#### Agent F3: Pattern Standardizer
```
Standardize inconsistent patterns: [PATTERNS_TO_FIX]

Tasks:
1. Update naming:
   - Apply consistent conventions
   - Fix prefixes/suffixes
   - Update references
   - Fix imports

2. Modernize syntax:
   - Update to latest patterns
   - Use modern features
   - Remove legacy code
   - Apply best practices

3. Align structure:
   - Consistent file organization
   - Standard export patterns
   - Uniform error handling
   - Common import order

Requirements:
- No breaking changes
- Gradual migration
- Maintain compatibility
```

#### Agent F4: Dead Code Remover
```
Remove unused code: [DEAD_CODE_TO_REMOVE]

Tasks:
1. Verify truly unused:
   - Double-check references
   - Check dynamic imports
   - Verify with tests
   - Check string references

2. Remove safely:
   - Delete unused files
   - Remove unused exports
   - Clean up imports
   - Update packages

3. Clean up:
   - Remove empty folders
   - Update index files
   - Clean package.json
   - Update documentation

Requirements:
- Only remove if certain
- Commit separately
- Verify builds work
```

#### Agent F5: Type Improver
```
Improve TypeScript types: [TYPES_TO_FIX]

Tasks:
1. Replace any types:
   - Infer correct types
   - Add explicit types
   - Use generics properly
   - Add type guards

2. Extract interfaces:
   - Create shared types
   - Build type hierarchy
   - Add discriminated unions
   - Export for reuse

3. Add missing types:
   - Function parameters
   - Return types
   - Event handlers
   - API responses

Requirements:
- No runtime changes
- Maintain compatibility
- Follow conventions
```

### Verification Agent
```
Verify all fixes were successful:

1. Run full test suite
2. Check build succeeds
3. Verify bundle size
4. Run linting
5. Check type coverage
6. Measure improvements

Generate final report with:
- Issues fixed
- Improvements achieved
- Remaining tech debt
- Next recommendations
```

## Configuration

### .techdebtignore
```
# Ignore patterns for tech debt analysis
vendor/
node_modules/
*.min.js
*.generated.ts
legacy/
__tests__/
```

### Custom Thresholds
```json
{
  "thresholds": {
    "duplication": {
      "minLines": 10,
      "minTokens": 50,
      "similarity": 0.7
    },
    "complexity": {
      "maxFileLines": 300,
      "maxFunctionLines": 30,
      "maxComplexity": 10
    },
    "types": {
      "minCoverage": 80,
      "allowAny": false
    }
  }
}
```

## Safety Features

1. **Pre-flight Checks**
   - Clean git status required
   - All tests must pass
   - Backup branch created

2. **Incremental Fixes**
   - One fix at a time
   - Test after each change
   - Easy rollback

3. **Review Mode**
   - Show before/after
   - Explain each change
   - Allow skipping

4. **Verification**
   - Automated testing
   - Build verification
   - Behavior validation

## Integration

### VS Code Command
```json
{
  "command": "claude.techDebtFinder",
  "title": "Find and Fix Tech Debt"
}
```

### Git Hook
```bash
#!/bin/sh
# Pre-push tech debt check
sub-agent-tech-debt-finder-fixer --dry-run --type duplicates
```

### CI/CD Pipeline
```yaml
tech-debt-check:
  script:
    - sub-agent-tech-debt-finder-fixer --dry-run
    - echo "Tech debt score: $(cat tech-debt-score.txt)"
  only:
    - merge_requests
```

## Best Practices

1. **Regular Scanning**: Run weekly to prevent accumulation
2. **Start Small**: Fix quick wins first to build momentum
3. **Test Coverage**: Ensure good tests before major refactoring
4. **Team Review**: Share reports in team meetings
5. **Track Progress**: Monitor debt score over time
6. **Gradual Improvement**: Don't try to fix everything at once