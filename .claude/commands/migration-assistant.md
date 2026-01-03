# Sub-Agent Migration Assistant Command

Assists with framework, library, and pattern migrations by analyzing code, creating migration plans, and safely implementing changes using specialized agents.

## Command Syntax

```bash
sub-agent-migration-assistant --from <source> --to <target> [options]

# Aliases
@migrate --from <source> --to <target> [options]
@migration-assistant [options]
@sama --from <source> --to <target> [options]
```

## Parameters

- `--from` - Source version/pattern (e.g., react@17, class-components)
- `--to` - Target version/pattern (e.g., react@18, hooks)
- `--target` - Directory to migrate (default: current)
- `--safe-mode` - Only apply safe migrations (default: true)
- `--pattern` - Specific pattern migration
- `--dry-run` - Show migration plan without changes
- `--incremental` - Migrate file by file
- `--compatibility` - Maintain backward compatibility
- `--test-after` - Run tests after each migration
- `--rollback-on-fail` - Auto rollback on test failure

## Examples

```bash
# React version migration
@migrate --from react@17 --to react@18 --safe-mode

# Pattern migration
@migrate --pattern class-to-hooks src/components/

# Laravel upgrade
@migrate --from laravel@8 --to laravel@10 --incremental

# Database migration
@migrate --from mysql@5.7 --to mysql@8.0 --dry-run
```

## Supported Migrations

### Frontend Migrations
- React 16 → 17 → 18
- Vue 2 → 3
- Angular version upgrades
- Class components → Hooks
- Redux → Context/Zustand
- JavaScript → TypeScript
- Webpack → Vite
- CSS → CSS Modules/Styled Components

### Backend Migrations
- Laravel 8 → 9 → 10
- PHP 7.x → 8.x
- Express → Fastify
- REST → GraphQL
- Callback → Promise → Async/Await

### Database Migrations
- MySQL version upgrades
- PostgreSQL migrations
- MongoDB schema updates
- SQL → NoSQL

## Agent Orchestration

### Stage 1: Analysis Agents (Parallel)

#### Agent 1: Deprecation Scanner
```
Scan for deprecated features in [TARGET] for [FROM_VERSION]

Tasks:
1. API Changes:
   - Deprecated methods
   - Removed functions
   - Changed signatures
   - Renamed properties
   - Modified behaviors

2. Syntax Changes:
   - Old syntax patterns
   - Deprecated operators
   - Changed keywords
   - Legacy patterns
   - Outdated imports

3. Dependencies:
   - Incompatible packages
   - Version conflicts
   - Deprecated dependencies
   - Breaking changes
   - Peer dependencies

4. Framework Specific:
   - React: Legacy lifecycle
   - Laravel: Deprecated facades
   - Vue: Options API usage
   - WordPress: Deprecated hooks

Return:
- Deprecation list with locations
- Breaking changes summary
- Required updates list
- Risk assessment
- Migration complexity
```

#### Agent 2: Compatibility Analyzer
```
Analyze compatibility requirements for migration

Tasks:
1. Dependency Tree:
   - Package compatibility
   - Version constraints
   - Transitive dependencies
   - Lock file analysis
   - Conflict resolution

2. Code Patterns:
   - Feature usage
   - API compatibility
   - Polyfill needs
   - Browser support
   - Runtime requirements

3. Testing Coverage:
   - Test framework compatibility
   - Assertion changes
   - Mock updates needed
   - Coverage gaps
   - E2E test impact

4. Infrastructure:
   - Server requirements
   - Build tool compatibility
   - CI/CD updates
   - Deployment changes
   - Environment variables

Return:
- Compatibility matrix
- Blocker identification
- Update sequence
- Polyfill requirements
- Infrastructure changes
```

#### Agent 3: Pattern Detector
```
Detect migration patterns in [TARGET]

Tasks:
1. Current Patterns:
   - Component patterns
   - State management
   - Routing approach
   - API integration
   - Error handling

2. Migration Paths:
   - Direct replacements
   - Refactor requirements
   - Gradual migration
   - Hybrid approaches
   - Codemod availability

3. Custom Patterns:
   - Project-specific code
   - Helper functions
   - Utility libraries
   - Business logic
   - Integration code

4. Edge Cases:
   - Complex migrations
   - Manual intervention
   - Partial migrations
   - Workarounds needed
   - Technical debt

Return:
- Pattern inventory
- Migration strategies
- Codemod applicability
- Manual work needed
- Edge case list
```

### Stage 2: Migration Planning Agent

```
Create migration plan from analyses: [ANALYSIS_RESULTS]

Tasks:
1. Sequencing:
   - Dependency order
   - Risk-based ordering
   - Incremental steps
   - Rollback points
   - Testing gates

2. Strategy Selection:
   - Big bang vs incremental
   - Feature flags usage
   - Parallel running
   - Gradual rollout
   - A/B testing approach

3. Risk Mitigation:
   - Backup strategies
   - Rollback procedures
   - Compatibility layers
   - Feature toggles
   - Monitoring plan

4. Resource Planning:
   - Time estimates
   - Team allocation
   - Testing requirements
   - Documentation needs
   - Training requirements

Generate:
- Step-by-step migration plan
- Risk mitigation strategies
- Rollback procedures
- Testing checklist
- Timeline estimate
```

### Stage 3: Implementation Agents (Parallel)

#### Agent 3A: Codemod Executor
```
Apply automated migrations using codemods

Tasks:
1. Codemod Selection:
   - Official codemods
   - Community codemods
   - Custom transforms
   - Safe transforms only
   - Verification needed

2. Execution:
   - Dry run first
   - Apply transforms
   - Verify output
   - Format code
   - Update imports

3. Validation:
   - Syntax checking
   - Type checking
   - Linting passes
   - Build succeeds
   - Tests pass

Example React Class to Hooks:
// Before
class UserProfile extends Component {
  state = { user: null };
  
  componentDidMount() {
    fetchUser().then(user => this.setState({ user }));
  }
  
  render() {
    return <div>{this.state.user?.name}</div>;
  }
}

// After
function UserProfile() {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetchUser().then(setUser);
  }, []);
  
  return <div>{user?.name}</div>;
}
```

#### Agent 3B: Manual Migration Handler
```
Handle complex migrations requiring manual intervention

Tasks:
1. Complex Patterns:
   - Custom implementations
   - Business logic updates
   - Integration changes
   - API adjustments
   - State management

2. Incremental Updates:
   - File-by-file migration
   - Component wrapping
   - Adapter patterns
   - Compatibility layers
   - Dual support

3. Testing Integration:
   - Update test files
   - Mock adjustments
   - Assertion updates
   - Coverage maintenance
   - E2E updates

Example Laravel Migration:
// Laravel 8
public function index(Request $request)
{
    return User::when($request->active, function ($query) {
        $query->where('active', true);
    })->get();
}

// Laravel 10
public function index(Request $request): JsonResponse
{
    return response()->json(
        User::when($request->boolean('active'), 
            fn ($query) => $query->active()
        )->get()
    );
}
```

#### Agent 3C: Dependency Updater
```
Update dependencies and handle conflicts

Tasks:
1. Package Updates:
   - Update versions
   - Resolve conflicts
   - Update lock files
   - Peer dependencies
   - Dev dependencies

2. Configuration Updates:
   - Build configs
   - Bundler settings
   - TypeScript config
   - Linting rules
   - Test configs

3. API Updates:
   - Import changes
   - Method updates
   - Property renames
   - Type updates
   - Default changes

Example package.json updates:
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@types/react": "^18.2.0"
  },
  "overrides": {
    "react": "$react",
    "react-dom": "$react-dom"
  }
}
```

### Stage 4: Verification Agent

```
Verify migration success and stability

Tasks:
1. Functional Testing:
   - Run test suites
   - Check coverage
   - E2E tests pass
   - Manual testing
   - User acceptance

2. Performance Testing:
   - Load time comparison
   - Memory usage
   - CPU utilization
   - Bundle size
   - Runtime performance

3. Compatibility Testing:
   - Browser testing
   - Device testing
   - API compatibility
   - Integration tests
   - Edge cases

4. Rollback Testing:
   - Rollback procedures
   - Data integrity
   - State preservation
   - Feature flags
   - Gradual rollout

Generate:
- Migration report
- Test results
- Performance comparison
- Issues found
- Recommendations
```

## Output Examples

### Migration Plan
```
📋 Migration Plan: React 17 → 18
=================================

Phase 1: Preparation (2 days)
✓ Update development environment
✓ Create migration branch
✓ Run full test suite baseline
✓ Document current patterns

Phase 2: Automated Migration (1 day)
→ Run React 18 codemods
  - ReactDOM.render → createRoot
  - Remove unnecessary Fragment
  - Update event handlers
→ Update dependencies
→ Fix TypeScript types

Phase 3: Manual Updates (3 days)
→ Update Suspense boundaries (12 files)
→ Fix StrictMode warnings (8 components)
→ Update test utilities
→ Refactor concurrent features

Phase 4: Testing & Validation (2 days)
→ Run updated test suite
→ Performance benchmarking
→ Browser compatibility testing
→ User acceptance testing

Total Estimate: 8 days
Risk Level: Medium
Rollback Strategy: Feature branch
```

### Migration Report
```
✅ Migration Complete: Class Components → Hooks
==============================================

📊 Summary
- Files Migrated: 47
- Components Updated: 89
- Lines Changed: 3,245
- Time Taken: 4.5 hours

🔄 Automated Migrations (85%)
- Simple class → function: 72 components
- Lifecycle → useEffect: 68 instances
- State → useState: 134 instances

✋ Manual Interventions (15%)
- Complex state logic: 8 components
- Higher-order components: 5 instances
- Render props patterns: 4 components

📈 Results
- Bundle Size: -12KB (compressed)
- Test Coverage: Maintained at 87%
- Performance: +5% faster renders
- Type Safety: Improved

⚠️ Follow-up Tasks
1. Update team documentation
2. Remove legacy utilities
3. Update coding standards
```

## Configuration

### .migration.config.js
```javascript
module.exports = {
  migrations: {
    'react@18': {
      codemods: [
        'react-18-upgrade-render',
        'react-18-strict-mode',
        'react-18-suspense-update'
      ],
      manualSteps: [
        'Update concurrent features',
        'Review Suspense boundaries',
        'Test automatic batching'
      ]
    },
    'laravel@10': {
      commands: [
        'composer update',
        'php artisan migrate',
        'php artisan config:cache'
      ],
      phpVersion: '8.1'
    }
  },
  
  testing: {
    runAfterEachFile: true,
    stopOnFailure: true,
    coverage: {
      threshold: 80
    }
  },
  
  rollback: {
    strategy: 'git',
    checkpoint: true
  }
};
```

## Best Practices

1. **Always Backup**: Create branches and backups before migration
2. **Test Continuously**: Run tests after each migration step
3. **Incremental Approach**: Migrate in small, testable chunks
4. **Document Changes**: Keep detailed migration logs
5. **Monitor Performance**: Compare before/after metrics
6. **Plan Rollback**: Always have a rollback strategy ready