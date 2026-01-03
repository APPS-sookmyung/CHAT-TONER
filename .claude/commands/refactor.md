# Sub-Agent Refactor Command

A powerful refactoring orchestrator that uses multiple specialized sub-agents to analyze, plan, implement, and verify code improvements while maintaining functionality.

## Command Syntax

```bash
sub-agent-refactor [target] [options]

# Aliases
@refactor [target] [options]
@sar [target] [options]
```

## Parameters

- `target` - File path, directory, or glob pattern to refactor (required)
- `--type` - Specific refactoring type (optional, defaults to auto-detect)
  - `extract-method` - Extract repeated code into methods/functions
  - `extract-component` - Break down large React/Vue components
  - `reduce-complexity` - Simplify complex functions
  - `consolidate-utils` - Merge duplicate utility functions
  - `organize-imports` - Clean up and organize imports
  - `remove-dead-code` - Remove unused code
  - `split-file` - Split large files into smaller modules
  - `standardize-patterns` - Fix inconsistent code patterns
  - `auto` - Let agents decide best refactoring approach

- `--max-function-size` - Maximum lines per function (default: 30)
- `--max-file-size` - Maximum lines per file (default: 300)
- `--max-complexity` - Maximum cyclomatic complexity (default: 10)
- `--create-shared` - Create shared utilities from duplicated code
- `--preserve-structure` - Maintain current file structure
- `--interactive` - Review each change before applying
- `--dry-run` - Show what would be changed without modifying files
- `--backup` - Create .bak files before changes (default: true)
- `--test-command` - Command to run tests (auto-detected if not specified)
- `--strict` - Fail if any test fails after refactoring

## Examples

### Basic Refactoring
```bash
# Auto-detect and refactor a single file
sub-agent-refactor src/components/UserDashboard.tsx

# Refactor an entire directory
sub-agent-refactor src/services/

# Use glob pattern
sub-agent-refactor "src/**/*Service.ts"
```

### Specific Refactoring Types
```bash
# Extract repeated code into shared utilities
sub-agent-refactor src/pages/ --type extract-method --create-shared

# Break down large React components
sub-agent-refactor src/components/Dashboard.tsx --type extract-component

# Reduce function complexity
sub-agent-refactor src/utils/calculations.ts --type reduce-complexity --max-function-size 20

# Consolidate duplicate utilities across project
sub-agent-refactor . --type consolidate-utils
```

### Advanced Usage
```bash
# Interactive mode with custom test command
sub-agent-refactor src/ --interactive --test-command "npm run test:unit"

# Dry run to preview changes
sub-agent-refactor src/api/ --dry-run --type reduce-complexity

# Strict mode with specific constraints
sub-agent-refactor src/ --strict --max-file-size 200 --max-complexity 8

# Refactor Laravel controllers
sub-agent-refactor app/Http/Controllers/ --type extract-method --create-shared
```

## Agent Orchestration

### Stage 1: Analysis Agent

**Prompt:**
```
Analyze the codebase at [TARGET] for refactoring opportunities.

Tasks:
1. Code Quality Analysis:
   - Identify code smells and anti-patterns
   - Find functions exceeding 30 lines
   - Find files exceeding 300 lines
   - Calculate cyclomatic complexity
   - Detect cognitive complexity issues

2. Duplication Detection:
   - Find exact duplicate code blocks
   - Identify similar code patterns (70%+ similarity)
   - Check for repeated business logic
   - Find duplicate utility functions
   - Identify copy-pasted code with minor variations

3. Pattern Analysis:
   - Check for inconsistent naming conventions
   - Find mixed paradigms (OOP vs functional)
   - Identify inconsistent error handling
   - Detect mixed async patterns (callbacks vs promises vs async/await)
   - Find inconsistent import structures

4. Dead Code Detection:
   - Unused variables and functions
   - Unreachable code blocks
   - Unused imports
   - Commented-out code blocks
   - Unused React components or Laravel services

5. Framework-Specific Issues:
   - React: Large components, prop drilling, missing memoization
   - Laravel: Fat controllers, missing service layer, N+1 queries
   - TypeScript: Excessive 'any' usage, missing types

Return a structured report with:
- Issues categorized by type and severity (Critical/High/Medium/Low)
- Risk assessment for each refactoring opportunity
- Estimated effort (Simple/Medium/Complex)
- Specific examples with file:line references
- Metrics summary (duplication %, average complexity, etc.)
```

### Stage 2: Planning Agent

**Prompt:**
```
Based on the analysis report: [ANALYSIS_RESULTS]
Create a comprehensive refactoring plan for [TARGET].

Planning Requirements:
1. Prioritization:
   - Order by impact vs effort ratio
   - Group related refactorings
   - Identify dependencies between changes
   - Start with lowest risk changes

2. Safety Considerations:
   - Ensure no behavior changes
   - Plan test coverage for changes
   - Identify potential breaking changes
   - Create rollback strategy

3. Architecture Decisions:
   - Where to place extracted utilities
   - How to split large files
   - Component hierarchy for extractions
   - Service layer organization

4. Naming Conventions:
   - Follow project's existing patterns
   - Use descriptive names
   - Maintain consistency

Generate a detailed plan including:
- Ordered list of refactoring tasks
- Specific files to create/modify/delete
- New directory structure if needed
- Migration strategy for imports
- Test points between major changes
- Rollback procedure for each step
- Example code snippets for clarity
```

### Stage 3: Implementation Agents (Parallel)

**Agent 3A - Utility Extractor:**
```
Extract shared utilities based on the plan: [EXTRACTION_PLAN]

Tasks:
1. Create new utility files in appropriate locations:
   - src/utils/ for general utilities
   - src/hooks/ for React hooks
   - app/Services/ for Laravel services

2. Extract duplicated code:
   - Parameterize differences
   - Add TypeScript types/PHP type hints
   - Include comprehensive JSDoc/PHPDoc
   - Handle edge cases properly

3. Update all references:
   - Import from new locations
   - Update relative paths
   - Fix any circular dependencies

Requirements:
- Follow existing code style exactly
- No functional changes allowed
- Add unit tests for new utilities
- Use descriptive function names
```

**Agent 3B - Component Refactorer:**
```
Refactor components/classes based on plan: [COMPONENT_PLAN]

Tasks:
1. Split large files:
   - Extract sub-components
   - Move types to separate files
   - Extract hooks to custom hooks
   - Separate concerns properly

2. Reduce complexity:
   - Extract complex conditionals
   - Break down large functions
   - Add early returns
   - Simplify nested structures

3. Maintain functionality:
   - Preserve all props/interfaces
   - Keep same behavior
   - Maintain event handlers
   - Preserve component lifecycle

Requirements:
- Use composition over inheritance
- Follow SOLID principles
- Maintain backwards compatibility
- Update all imports and exports
```

**Agent 3C - Pattern Standardizer:**
```
Standardize code patterns based on plan: [PATTERN_PLAN]

Tasks:
1. Fix naming inconsistencies:
   - Event handlers: prefix with 'handle'
   - Booleans: prefix with 'is/has/should'
   - Constants: UPPER_SNAKE_CASE
   - Files: consistent casing

2. Standardize async patterns:
   - Convert callbacks to promises
   - Use async/await consistently
   - Proper error handling

3. Framework patterns:
   - React: hooks usage, component structure
   - Laravel: repository pattern, service layer
   - Consistent dependency injection

Requirements:
- Don't change functionality
- Update gradually to avoid conflicts
- Maintain readability
```

### Stage 4: Verification Agent

**Prompt:**
```
Verify the refactoring of [TARGET] was successful.

Verification Tasks:
1. Functionality Testing:
   - Run existing test suite: [TEST_COMMAND]
   - Check for any failing tests
   - Verify no runtime errors
   - Test critical user paths

2. Code Quality Metrics:
   - Measure complexity reduction
   - Calculate new duplication percentage
   - Check file/function sizes
   - Verify type coverage improvement

3. Integration Verification:
   - All imports resolve correctly
   - No circular dependencies
   - Build completes successfully
   - Linting passes

4. Performance Check:
   - Bundle size comparison
   - Build time comparison
   - Runtime performance (if measurable)

5. Visual Verification (for UI):
   - Components render correctly
   - No visual regressions
   - Styles applied properly

Generate report with:
- Test results summary
- Before/after metrics comparison
- Any issues found
- Rollback recommendation if needed
- Suggested next steps
```

## Error Handling

### Common Issues and Solutions

**Issue:** Tests fail after refactoring
```bash
# Run with interactive mode to review changes
sub-agent-refactor [target] --interactive

# Or increase test coverage first
sub-agent-refactor [target] --dry-run
```

**Issue:** Circular dependency created
```bash
# Use preserve-structure to avoid moving files
sub-agent-refactor [target] --preserve-structure
```

**Issue:** Performance degradation
```bash
# Run with performance monitoring
sub-agent-refactor [target] --profile
```

## Integration Examples

### VSCode Task
```json
{
  "label": "Refactor Current File",
  "type": "shell",
  "command": "sub-agent-refactor ${file} --interactive",
  "group": "build"
}
```

### Git Pre-commit Hook
```bash
#!/bin/sh
# Check for refactoring opportunities
sub-agent-refactor src/ --dry-run --type auto
```

### CI/CD Pipeline
```yaml
- name: Code Quality Check
  run: |
    sub-agent-refactor src/ --dry-run
    if [ $? -ne 0 ]; then
      echo "Refactoring opportunities found"
      exit 1
    fi
```

## Best Practices

1. **Start Small:** Begin with a single file or small directory
2. **Use Dry Run:** Always preview changes first
3. **Have Tests:** Ensure good test coverage before refactoring
4. **Commit Before:** Clean git state before refactoring
5. **Review Changes:** Use interactive mode for critical code
6. **Incremental:** Refactor in small, reviewable chunks

## Framework-Specific Notes

### React/TypeScript
- Automatically handles JSX syntax
- Preserves component props interfaces
- Maintains hook dependencies
- Respects memo/callback optimizations

### Laravel/PHP
- Follows PSR standards
- Maintains service provider registrations
- Updates route definitions
- Preserves middleware chains

### WordPress
- Maintains action/filter hooks
- Preserves plugin structure
- Updates function prefixes
- Keeps backwards compatibility