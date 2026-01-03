# Sub-Agent Performance Optimizer Command

Optimizes application performance across the entire stack using specialized agents for frontend, backend, database, and infrastructure optimization.

## Command Syntax

```bash
sub-agent-performance-optimizer [target] [options]

# Aliases
@perf-optimize [target] [options]
@performance [target] [options]
@sapo [target] [options]
```

## Parameters

- `target` - Directory or specific area to optimize
- `--target` - Optimization target (frontend, backend, database, all)
- `--bundle-analysis` - Analyze JavaScript bundles
- `--suggest-indexes` - Database index recommendations
- `--baseline` - Compare against performance baseline
- `--profile` - Generate performance profiles
- `--tree-shake` - Aggressive tree shaking
- `--cache-strategy` - Generate caching recommendations
- `--output` - Report format (text, json, html)
- `--auto-fix` - Apply safe optimizations

## Examples

```bash
# Frontend bundle optimization
@perf-optimize src/ --target frontend --bundle-analysis

# Database query optimization
@perf-optimize --target database --suggest-indexes

# Full stack optimization
@performance . --baseline perf-baseline.json

# WordPress specific optimization
@perf-optimize wp-content/ --target wordpress --cache-strategy
```

## Agent Orchestration

### Stage 1: Analysis Agents (Parallel)

#### Agent 1: Frontend Performance Analyzer
```
Analyze frontend performance in [TARGET]

Tasks:
1. Bundle Analysis:
   - Bundle sizes by chunk
   - Duplicate modules
   - Tree shaking opportunities
   - Code splitting points
   - Unused exports
   - Large dependencies

2. React/Component Performance:
   - Unnecessary re-renders
   - Missing React.memo
   - useCallback/useMemo opportunities
   - Large component trees
   - Expensive computations
   - State management overhead

3. Asset Optimization:
   - Unoptimized images
   - Missing lazy loading
   - Font loading strategy
   - CSS optimization
   - Script loading order
   - Resource hints missing

4. Runtime Performance:
   - Long tasks (>50ms)
   - Memory leaks
   - DOM manipulation cost
   - Event listener overhead
   - Animation performance
   - Third-party impact

Return:
- Bundle size breakdown
- Performance bottlenecks
- Optimization opportunities
- Load time analysis
- Runtime metrics
```

#### Agent 2: Backend Performance Analyzer
```
Analyze backend performance in [TARGET]

Tasks:
1. API Performance:
   - Response time analysis
   - N+1 query detection
   - Slow endpoints
   - Payload sizes
   - Serialization overhead
   - Rate limiting needs

2. Laravel/PHP Specific:
   - Eager loading missing
   - Query builder inefficiency
   - Cache opportunities
   - Queue usage
   - Service container overhead
   - Middleware performance

3. Cloudflare Workers:
   - Cold start times
   - KV/D1 query patterns
   - Subrequest optimization
   - CPU time usage
   - Memory consumption
   - Bundle size impact

4. Resource Usage:
   - Memory patterns
   - CPU hotspots
   - I/O bottlenecks
   - Connection pooling
   - Background job impact
   - External API calls

Return:
- Slow endpoint list
- Query optimization needs
- Caching opportunities
- Resource usage patterns
- Scaling recommendations
```

#### Agent 3: Database Performance Analyzer
```
Analyze database performance for [TARGET]

Tasks:
1. Query Analysis:
   - Slow queries (>100ms)
   - Missing indexes
   - Full table scans
   - Inefficient joins
   - Subquery optimization
   - Query plan analysis

2. Schema Optimization:
   - Table structure
   - Data types efficiency
   - Normalization issues
   - Missing foreign keys
   - Unused indexes
   - Partition opportunities

3. Laravel Specific:
   - Eloquent N+1 problems
   - Missing eager loading
   - Chunk processing needs
   - Migration efficiency
   - Relationship optimization
   - Scope performance

4. Database Health:
   - Lock contention
   - Connection pool size
   - Cache hit ratio
   - Transaction duration
   - Replication lag
   - Storage growth

Return:
- Query optimization list
- Index recommendations
- Schema improvements
- Configuration tuning
- Scaling strategies
```

#### Agent 4: Caching Strategy Analyzer
```
Analyze caching opportunities in [TARGET]

Tasks:
1. Cache Coverage:
   - Uncached queries
   - Static content caching
   - API response caching
   - Session caching
   - Object caching
   - Page caching

2. Cache Effectiveness:
   - Hit/miss ratios
   - TTL optimization
   - Cache key strategy
   - Invalidation patterns
   - Memory usage
   - Stale data risks

3. CDN Optimization:
   - Static asset delivery
   - Edge caching rules
   - Geographic distribution
   - Compression settings
   - Header optimization
   - Purge strategies

4. Application Caching:
   - Redis/Memcached usage
   - In-memory caching
   - Database query cache
   - OPcache configuration
   - APCu optimization
   - Cache warming needs

Return:
- Caching strategy plan
- Implementation priority
- TTL recommendations
- Invalidation rules
- Memory requirements
```

### Stage 2: Optimization Planning Agent

```
Create optimization plan from all analyses: [PERFORMANCE_ANALYSES]

Tasks:
1. Impact Assessment:
   - Performance gain estimates
   - Implementation effort
   - Risk evaluation
   - Dependencies
   - Quick wins identification

2. Optimization Roadmap:
   - Priority order
   - Batch related fixes
   - Progressive enhancement
   - Rollback strategies
   - Testing requirements

3. Resource Planning:
   - Memory impact
   - CPU requirements
   - Network usage
   - Storage needs
   - Cost implications

4. Monitoring Strategy:
   - Key metrics to track
   - Baseline establishment
   - Alert thresholds
   - Performance budgets
   - Regression detection

Generate:
- Prioritized optimization list
- Implementation guide
- Performance budget
- Monitoring setup
- Success metrics
```

### Stage 3: Implementation Agents (Parallel)

#### Agent 3A: Frontend Optimizer
```
Implement frontend optimizations from [FRONTEND_PLAN]

Optimizations:
1. Bundle Optimization:
   - Configure code splitting
   - Implement tree shaking
   - Remove unused code
   - Optimize imports
   - Lazy load components
   - Extract common chunks

2. React Optimization:
   - Add React.memo
   - Implement useMemo/useCallback
   - Optimize context usage
   - Split large components
   - Virtualize long lists
   - Debounce updates

3. Asset Optimization:
   - Compress images
   - Implement lazy loading
   - Optimize fonts
   - Minify CSS/JS
   - Add resource hints
   - Configure CDN

Example implementations...
```

#### Agent 3B: Backend Optimizer
```
Implement backend optimizations from [BACKEND_PLAN]

Optimizations:
1. Query Optimization:
   - Add eager loading
   - Optimize joins
   - Implement caching
   - Add indexes
   - Batch operations
   - Use query builder efficiently

2. API Optimization:
   - Implement pagination
   - Add field filtering
   - Compress responses
   - Cache headers
   - Rate limiting
   - Async processing

3. Laravel Specific:
   - Route caching
   - Config caching
   - View caching
   - Query optimization
   - Job queuing
   - Service optimization

Example implementations...
```

#### Agent 3C: Database Optimizer
```
Implement database optimizations from [DATABASE_PLAN]

Optimizations:
1. Index Creation:
   - Analyze query patterns
   - Create optimal indexes
   - Remove unused indexes
   - Composite indexes
   - Covering indexes
   - Partial indexes

2. Query Rewriting:
   - Optimize complex queries
   - Remove subqueries
   - Use proper joins
   - Batch operations
   - Stored procedures
   - View optimization

3. Schema Updates:
   - Normalize tables
   - Add constraints
   - Optimize data types
   - Partition tables
   - Archive old data
   - Compression settings

Example implementations...
```

## Output Examples

### Performance Report
```
🚀 Performance Optimization Report
==================================

📊 Current Performance
- Page Load Time: 4.2s
- Time to Interactive: 6.8s
- API Response (avg): 320ms
- Database Queries (avg): 89ms

🎯 Optimizations Applied

Frontend (Impact: -2.1s load time):
✓ Code splitting implemented (5 chunks)
✓ Tree shaking reduced bundle by 34%
✓ Images lazy loaded (saved 1.2MB)
✓ React.memo added to 12 components

Backend (Impact: -180ms response time):
✓ Added eager loading to 8 queries
✓ Implemented Redis caching
✓ Optimized serialization
✓ Added API response compression

Database (Impact: -45ms query time):
✓ Added 5 missing indexes
✓ Optimized 3 complex queries
✓ Implemented query result caching
✓ Fixed N+1 in user queries

📈 New Performance
- Page Load Time: 2.1s (-50%)
- Time to Interactive: 3.2s (-53%)
- API Response (avg): 140ms (-56%)
- Database Queries (avg): 44ms (-51%)

🔧 Remaining Opportunities
1. Implement service worker (est. -0.5s)
2. Add image CDN (est. -0.3s)
3. Database partitioning (est. -20ms)
```

### Bundle Analysis Report
```
📦 Bundle Analysis
==================

Main Bundle: 245KB (gzipped)
├── react-dom: 42KB (17%)
├── lodash: 28KB (11%)
├── moment: 22KB (9%)
├── app code: 89KB (36%)
└── other deps: 64KB (26%)

Recommendations:
1. Replace moment with date-fns (-18KB)
2. Import only needed lodash functions (-20KB)
3. Lazy load admin features (-35KB)

Unused Exports Found:
- src/utils/helpers.js: 5 unused functions
- src/components/index.js: 3 unused exports
```

### Database Optimization Script
```sql
-- Generated indexes for optimal performance
CREATE INDEX idx_users_email_active ON users(email, active);
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at DESC);
CREATE INDEX idx_products_category_price ON products(category_id, price);

-- Query optimization example
-- Before (320ms):
SELECT * FROM orders o 
WHERE user_id IN (SELECT id FROM users WHERE active = 1);

-- After (45ms):
SELECT o.* FROM orders o
INNER JOIN users u ON o.user_id = u.id
WHERE u.active = 1;
```

## Configuration

### .performance.config.js
```javascript
module.exports = {
  targets: {
    pageLoad: 3000,      // 3s target
    timeToInteractive: 5000,
    apiResponse: 200,    // 200ms target
    databaseQuery: 50    // 50ms target
  },
  
  frontend: {
    bundleSizeLimit: 300000,  // 300KB
    chunkSizeLimit: 50000,    // 50KB per chunk
    imageOptimization: {
      quality: 85,
      formats: ['webp', 'avif']
    }
  },
  
  backend: {
    cacheStrategy: 'aggressive',
    compressionLevel: 6,
    rateLimit: {
      window: 60000,  // 1 minute
      max: 100
    }
  },
  
  monitoring: {
    metrics: ['LCP', 'FID', 'CLS', 'TTFB'],
    alerts: {
      pageLoad: { threshold: 4000, severity: 'warning' },
      apiResponse: { threshold: 500, severity: 'critical' }
    }
  }
};
```

## Best Practices

1. **Measure First**: Always baseline before optimizing
2. **Incremental Changes**: Apply one optimization at a time
3. **Monitor Impact**: Track metrics after each change
4. **Set Budgets**: Define performance budgets
5. **Automate Checks**: Add to CI/CD pipeline
6. **User-Centric**: Focus on user-perceived performance