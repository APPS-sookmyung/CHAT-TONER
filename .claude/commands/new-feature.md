# Sub-Agent New Feature Command

Orchestrates multiple specialized sub-agents to implement new features efficiently by analyzing existing patterns, checking dependencies, and maximizing code reuse.

## Command Syntax

```bash
sub-agent-new-feature --feature "<description>" --location "<target>" [options]

# Aliases
@new-feature --feature "<description>" --location "<target>" [options]
@sanf --feature "<description>" --location "<target>" [options]
```

## Parameters

### Required Parameters
- `--feature` - Clear description of the feature to implement
- `--location` - Target directory or file where the feature should be added

### Optional Parameters
- `--type` - Feature type (component, api, full-stack, worker, plugin)
- `--tech-stack` - Override detected stack (react, laravel, wordpress, cloudflare)
- `--reuse-only` - Only use existing code, fail if new dependencies needed
- `--package-search` - Search for packages before implementing (default: true)
- `--test-first` - Generate tests before implementation
- `--parallel` - Number of parallel implementation agents (default: 3)
- `--review-mode` - Code review strictness (strict, standard, fast)
- `--docs` - Generate documentation (inline, separate, both, none)
- `--style-guide` - Path to custom style guide
- `--example-files` - Reference files for patterns to follow

## Examples

### Basic Usage
```bash
# Add a user profile component
sub-agent-new-feature --feature "User profile card with avatar, name, and stats" --location src/components/

# Add an API endpoint
sub-agent-new-feature --feature "API endpoint to export orders as CSV" --location app/Http/Controllers/

# Add a Cloudflare Worker
sub-agent-new-feature --feature "Image optimization worker" --location functions/
```

### Advanced Usage
```bash
# Full-stack feature with tests
sub-agent-new-feature \
  --feature "Comment system with real-time updates" \
  --location src/features/comments \
  --type full-stack \
  --test-first \
  --parallel 5

# WordPress plugin feature
sub-agent-new-feature \
  --feature "Custom shipping calculator widget" \
  --location wp-content/plugins/my-plugin \
  --tech-stack wordpress \
  --docs both

# Strict review mode with examples
sub-agent-new-feature \
  --feature "Data table with sorting and filtering" \
  --location src/components/tables \
  --review-mode strict \
  --example-files "src/components/UserTable.tsx,src/components/OrderTable.tsx"
```

## Stage 1: Analysis Agents (Parallel)

### Agent 1A: Pattern Analyzer
```
Analyze existing codebase patterns for implementing: [FEATURE_DESCRIPTION]
Target location: [LOCATION]

Tasks:
1. Search for similar features/components:
   - Find existing implementations with similar functionality
   - Identify UI patterns used (for components)
   - Find API patterns used (for endpoints)
   - Locate similar business logic

2. Extract reusable elements:
   - Common utility functions
   - Shared components (buttons, modals, forms)
   - Existing hooks or services
   - Database queries or models

3. Identify coding patterns:
   - Component structure (functional vs class)
   - State management approach
   - Error handling patterns
   - Testing patterns

4. Framework-specific patterns:
   - React: Context usage, custom hooks, component composition
   - Laravel: Service patterns, middleware usage, validation
   - WordPress: Hook usage, plugin structure, database access
   - Cloudflare: Worker patterns, KV usage, request handling

Return:
- List of similar implementations with file paths
- Reusable components/utilities to leverage
- Coding patterns to follow
- Do's and don'ts based on existing code
```

### Agent 1B: Dependency Checker
```
Check for existing packages and dependencies for: [FEATURE_DESCRIPTION]

Tasks:
1. Analyze current dependencies:
   - Check package.json/composer.json
   - Find packages already used for similar features
   - Identify underutilized packages

2. Search for new packages (if allowed):
   - Search npm/packagist for feature-specific packages
   - Evaluate package quality (downloads, maintenance, size)
   - Check license compatibility
   - Review security advisories

3. Cost-benefit analysis:
   - Bundle size impact for frontend packages
   - Performance implications
   - Maintenance burden
   - Learning curve

4. Internal alternatives:
   - Can we build with existing dependencies?
   - Are we already using something similar?
   - Would a small utility be better than a package?

Return:
- Recommended packages to use (existing or new)
- Implementation approach with each package
- Size/performance impact assessment
- Alternative approaches without new dependencies
```

### Agent 1C: Technical Feasibility Analyzer
```
Assess technical requirements for: [FEATURE_DESCRIPTION]
In location: [LOCATION]

Tasks:
1. Architecture fit:
   - How does this fit current architecture?
   - Any architectural changes needed?
   - Impact on existing systems

2. Data requirements:
   - Database schema changes needed?
   - API contracts to define?
   - State management considerations

3. Performance implications:
   - Client-side performance impact
   - Server-side load considerations
   - Caching opportunities

4. Security considerations:
   - Authentication/authorization needs
   - Input validation requirements
   - Data privacy concerns

5. Integration points:
   - External APIs needed?
   - WebSocket/real-time requirements?
   - File upload/processing needs?

Return:
- Technical requirements list
- Potential challenges and solutions
- Performance optimization opportunities
- Security checklist
```

## Stage 2: Planning & Architecture Agent

```
Synthesize analysis from all Stage 1 agents: [ANALYSIS_RESULTS]
Create implementation plan for: [FEATURE_DESCRIPTION]

Planning tasks:
1. Architecture design:
   - Component/service structure
   - Data flow diagram
   - State management approach
   - API design (if applicable)

2. File structure:
   - New files to create
   - Existing files to modify
   - Directory organization
   - Naming conventions

3. Implementation approach:
   - Prioritize reusing existing code
   - Minimize new dependencies
   - Follow established patterns
   - Plan for extensibility

4. Task breakdown:
   - Ordered list of implementation steps
   - Dependencies between tasks
   - Parallel vs sequential work
   - Testing points

5. Risk mitigation:
   - Identify potential breaking changes
   - Plan for backwards compatibility
   - Error handling strategy
   - Rollback plan

Generate:
- Detailed implementation plan
- Component/API specifications
- File structure diagram
- Task list for implementation agents
- Code snippets for complex parts
```

## Stage 3: Implementation Agents (Parallel)

### Agent 3A: UI Component Builder (React/Frontend)
```
Implement frontend components for: [COMPONENT_SPEC]
Following plan: [IMPLEMENTATION_PLAN]

Requirements:
1. Use existing component library:
   - Leverage shadcn/ui components
   - Follow Tailwind patterns
   - Reuse existing components

2. Component structure:
   - TypeScript interfaces for all props
   - Proper component composition
   - Event handler naming (handleX)
   - Accessibility features (ARIA)

3. State management:
   - Use existing patterns (Context, Redux, etc.)
   - Custom hooks for logic
   - Proper memoization

4. Styling approach:
   - Tailwind classes (no inline styles)
   - Follow existing naming patterns
   - Responsive design
   - Dark mode support

5. Code quality:
   - No placeholders or TODOs
   - Complete error handling
   - Loading states
   - Empty states

Output complete, working components with all imports.
```

### Agent 3B: API Endpoint Builder (Laravel/Backend)
```
Implement API endpoints for: [API_SPEC]
Following plan: [IMPLEMENTATION_PLAN]

Requirements:
1. Follow Laravel patterns:
   - Use existing middleware
   - Leverage service classes
   - Proper validation rules
   - Resource transformers

2. Database operations:
   - Use existing models/relationships
   - Optimize queries (avoid N+1)
   - Use transactions where needed
   - Proper indexing

3. Business logic:
   - Extract to service classes
   - Use existing utilities
   - Follow DRY principles
   - Dependency injection

4. Error handling:
   - Consistent error responses
   - Proper HTTP status codes
   - Validation messages
   - Logging

5. Security:
   - Authorization checks
   - Input sanitization
   - Rate limiting
   - CORS handling

Output complete controllers, services, and routes.
```

### Agent 3C: Worker/Edge Function Builder (Cloudflare)
```
Implement Cloudflare Worker for: [WORKER_SPEC]
Following plan: [IMPLEMENTATION_PLAN]

Requirements:
1. Worker patterns:
   - Use Hono router if applicable
   - Leverage existing middleware
   - Proper request handling
   - Response formatting

2. Storage usage:
   - KV for key-value data
   - D1 for relational data
   - R2 for object storage
   - Cache API for performance

3. Performance:
   - Minimize cold starts
   - Efficient bundling
   - Proper caching strategies
   - Request/response streaming

4. Error handling:
   - Graceful degradation
   - Proper error responses
   - Retry logic
   - Dead letter queues

5. Security:
   - Request validation
   - Authentication/authorization
   - Rate limiting
   - CORS policies

Output complete worker with all dependencies.
```

### Agent 3D: Test Generator
```
Generate tests for: [FEATURE_COMPONENTS]
Following patterns in: [EXISTING_TESTS]

Requirements:
1. Unit tests:
   - Test individual functions
   - Mock dependencies
   - Edge cases
   - Error scenarios

2. Integration tests:
   - API endpoint tests
   - Database operations
   - Service interactions

3. Component tests:
   - Render tests
   - User interactions
   - State changes
   - Accessibility

4. E2E tests (if applicable):
   - User workflows
   - Critical paths
   - Cross-browser

Output complete test files with all assertions.
```

## Stage 4: Integration & Review Agent

```
Review and integrate all generated code from Stage 3 agents.

Integration tasks:
1. Code review:
   - Check all imports are correct
   - Verify naming consistency
   - Ensure no duplicated code
   - Validate TypeScript types

2. Integration verification:
   - All components connect properly
   - API endpoints match frontend calls
   - Error handling is consistent
   - State management works end-to-end

3. Pattern compliance:
   - Follows project conventions
   - Uses existing utilities
   - No unnecessary dependencies
   - Consistent error handling

4. Performance review:
   - Bundle size impact
   - Query optimization
   - Caching implementation
   - Loading performance

5. Security review:
   - Input validation
   - Authentication checks
   - XSS prevention
   - SQL injection prevention

6. Testing:
   - All tests pass
   - Adequate coverage
   - Edge cases handled

Generate:
- Integration report
- Any fixes needed
- Performance metrics
- Final code adjustments
- Deployment notes
```

## Advanced Configuration

### Custom Style Guide
```bash
# Use specific style guide
sub-agent-new-feature \
  --feature "Custom dashboard" \
  --location src/dashboards \
  --style-guide ./docs/style-guide.md
```

### CI/CD Integration
```yaml
# GitHub Action example
- name: Generate Feature
  run: |
    npx claude-code sub-agent-new-feature \
      --feature "${{ inputs.feature }}" \
      --location "${{ inputs.location }}" \
      --review-mode strict \
      --test-first
```

### Package Search Configuration
```bash
# Disable package search for airgapped environments
sub-agent-new-feature \
  --feature "Offline data sync" \
  --location src/sync \
  --package-search false \
  --reuse-only
```

## Error Handling

### Common Issues

**Issue**: No similar patterns found
**Solution**: Provide example files or create initial pattern

**Issue**: Package conflicts
**Solution**: Use `--reuse-only` to avoid new dependencies

**Issue**: Tests failing
**Solution**: Use `--test-first` to ensure testability

## Best Practices

1. **Clear Feature Description**: Be specific about requirements
2. **Provide Examples**: Use `--example-files` for complex features
3. **Start Small**: Build incrementally for large features
4. **Review Mode**: Use strict mode for critical features
5. **Test First**: Generate tests before implementation
6. **Document**: Use `--docs both` for public APIs