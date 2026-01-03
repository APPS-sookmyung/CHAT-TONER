# Sub-Agent Test Generator Command

Generates comprehensive test suites by analyzing code patterns, identifying untested paths, and creating meaningful test cases using multiple specialized agents.

## Command Syntax

```bash
sub-agent-test-generator [target] [options]

# Aliases
@test-gen [target] [options]
@test-generator [target] [options]
@satg [target] [options]
```

## Parameters

- `target` - Files or directories to generate tests for
- `--coverage-target` - Target coverage percentage (default: 80)
- `--type` - Test types (unit, integration, e2e, all)
- `--framework` - Test framework (jest, phpunit, playwright, cypress)
- `--only-untested` - Only generate for untested code
- `--from-flows` - Generate from user flow analysis
- `--mock-strategy` - Mocking approach (minimal, realistic, full)
- `--assertions` - Assertion style (expect, should, assert)
- `--update-existing` - Update existing tests
- `--edge-cases` - Include edge case testing

## Examples

```bash
# Generate missing unit tests
@test-gen src/services/ --only-untested

# Generate tests with 90% coverage target
@test-gen src/ --coverage-target 90 --type unit

# Generate E2E tests from user flows
@test-gen --type e2e --from-flows src/features/

# Update existing tests with edge cases
@test-gen src/utils/ --update-existing --edge-cases
```

## Agent Orchestration

### Stage 1: Analysis Agents (Parallel)

#### Agent 1: Coverage Analyzer
```
Analyze test coverage in [TARGET]

Tasks:
1. Coverage Metrics:
   - Line coverage
   - Branch coverage
   - Function coverage
   - Statement coverage
   - Path coverage

2. Untested Code:
   - Functions without tests
   - Uncovered branches
   - Error paths not tested
   - Edge cases missing
   - Integration gaps

3. Test Quality:
   - Assertion density
   - Mock coverage
   - Test isolation
   - Setup/teardown patterns
   - Test naming

4. Critical Paths:
   - Business logic coverage
   - Error handling coverage
   - Security function coverage
   - Data validation coverage
   - API endpoint coverage

Return:
- Coverage report by file
- Untested functions list
- Critical gap analysis
- Test quality metrics
- Priority test targets
```

#### Agent 2: Code Path Analyzer
```
Analyze code paths and behaviors in [TARGET]

Tasks:
1. Function Analysis:
   - Input parameters
   - Return values
   - Side effects
   - Dependencies
   - Error conditions

2. Branch Analysis:
   - Conditional branches
   - Loop variations
   - Switch cases
   - Try-catch blocks
   - Early returns

3. State Analysis:
   - State mutations
   - Class properties
   - Global state usage
   - Context dependencies
   - Lifecycle methods

4. Integration Points:
   - API calls
   - Database queries
   - File operations
   - External services
   - Event emissions

Return:
- Function behavior map
- Branch conditions
- State dependencies
- Integration points
- Test scenarios needed
```

#### Agent 3: Pattern Recognizer
```
Identify testing patterns and conventions in [TARGET]

Tasks:
1. Existing Patterns:
   - Test file structure
   - Naming conventions
   - Setup patterns
   - Assertion styles
   - Mock patterns

2. Framework Usage:
   - Test runner config
   - Assertion library
   - Mocking library
   - Helper utilities
   - Custom matchers

3. Best Practices:
   - AAA pattern usage
   - Test isolation
   - DRY in tests
   - Descriptive names
   - Error scenarios

4. Anti-patterns:
   - Overmocking
   - Brittle tests
   - Large setup
   - Unclear assertions
   - Missing cleanup

Return:
- Pattern guide
- Convention rules
- Framework config
- Style preferences
- Improvement areas
```

### Stage 2: Test Generation Agents (Parallel)

#### Agent 2A: Unit Test Generator
```
Generate unit tests for [FUNCTIONS] following [PATTERNS]

Tasks:
1. Test Structure:
   - Create test files
   - Import dependencies
   - Setup test suites
   - Add descriptions
   - Group related tests

2. Test Cases:
   - Happy path tests
   - Error scenarios
   - Edge cases
   - Boundary values
   - Null/undefined handling

3. Assertions:
   - Return value checks
   - State verifications
   - Error validations
   - Call verifications
   - Side effect checks

4. Mocking:
   - Mock dependencies
   - Stub external calls
   - Spy on methods
   - Mock timers/dates
   - Reset mocks

Example Output:
describe('UserService', () => {
  let userService;
  let mockRepo;

  beforeEach(() => {
    mockRepo = createMockRepository();
    userService = new UserService(mockRepo);
  });

  describe('createUser', () => {
    it('should create user with valid data', async () => {
      const userData = { name: 'John', email: 'john@example.com' };
      mockRepo.save.mockResolvedValue({ id: 1, ...userData });

      const result = await userService.createUser(userData);

      expect(result).toHaveProperty('id');
      expect(mockRepo.save).toHaveBeenCalledWith(userData);
    });

    it('should throw error for duplicate email', async () => {
      mockRepo.save.mockRejectedValue(new Error('Duplicate email'));

      await expect(userService.createUser({}))
        .rejects.toThrow('Duplicate email');
    });
  });
});
```

#### Agent 2B: Integration Test Generator
```
Generate integration tests for [COMPONENTS] with [DEPENDENCIES]

Tasks:
1. Test Setup:
   - Database setup
   - API mocking
   - Service initialization
   - Test data preparation
   - Environment config

2. Scenarios:
   - Multi-step workflows
   - Service interactions
   - Data persistence
   - Transaction handling
   - Error propagation

3. Verifications:
   - End-to-end flow
   - Data integrity
   - State consistency
   - Response format
   - Performance bounds

4. Cleanup:
   - Database cleanup
   - Reset mocks
   - Clear caches
   - Restore state
   - Close connections

Example Output:
describe('Order Processing Integration', () => {
  let app;
  let db;

  beforeAll(async () => {
    db = await setupTestDatabase();
    app = await createTestApp(db);
  });

  afterAll(async () => {
    await db.close();
  });

  it('should process order from cart to completion', async () => {
    // Arrange
    const user = await createTestUser();
    const products = await createTestProducts();
    
    // Act
    const cart = await addToCart(user.id, products);
    const order = await checkoutCart(cart.id);
    const payment = await processPayment(order.id);
    
    // Assert
    expect(order.status).toBe('completed');
    expect(payment.status).toBe('successful');
    
    const savedOrder = await db.orders.findById(order.id);
    expect(savedOrder.items).toHaveLength(products.length);
  });
});
```

#### Agent 2C: E2E Test Generator
```
Generate end-to-end tests for [USER_FLOWS]

Tasks:
1. Flow Analysis:
   - User journeys
   - Page interactions
   - Form submissions
   - Navigation paths
   - Error scenarios

2. Test Scripts:
   - Browser automation
   - Element selection
   - Action sequences
   - Assertions
   - Screenshots

3. Data Setup:
   - Test accounts
   - Seed data
   - API mocks
   - External services
   - Reset scripts

4. Validations:
   - Visual checks
   - Content verification
   - State validation
   - Performance metrics
   - Accessibility

Example Output:
describe('User Registration Flow', () => {
  beforeEach(async () => {
    await page.goto('/register');
  });

  it('should complete registration successfully', async () => {
    // Fill registration form
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'SecurePass123!');
    await page.fill('[name="confirmPassword"]', 'SecurePass123!');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Verify redirect and welcome message
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('.welcome-message'))
      .toContainText('Welcome to the platform!');
    
    // Verify user can access protected routes
    await page.goto('/profile');
    await expect(page.locator('.user-email'))
      .toContainText('test@example.com');
  });

  it('should show validation errors', async () => {
    await page.fill('[name="email"]', 'invalid-email');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.error-message'))
      .toContainText('Please enter a valid email');
  });
});
```

### Stage 3: Test Optimizer Agent

```
Optimize generated tests from [GENERATED_TESTS]

Tasks:
1. Remove Redundancy:
   - Combine similar tests
   - Extract common setup
   - Create test utilities
   - Reduce duplication

2. Improve Maintainability:
   - Add data builders
   - Create page objects
   - Extract constants
   - Improve naming

3. Enhance Coverage:
   - Add missing edges
   - Include error paths
   - Test concurrency
   - Add performance tests

4. Documentation:
   - Add test descriptions
   - Document prerequisites
   - Explain complex mocks
   - Add usage examples

Return:
- Optimized test suite
- Shared utilities
- Test helpers
- Documentation
```

## Configuration

### .testgen.config.js
```javascript
module.exports = {
  unit: {
    framework: 'jest',
    testMatch: ['**/*.test.js'],
    mockStyle: 'jest.fn',
    assertionStyle: 'expect',
    coverageThreshold: {
      global: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80
      }
    }
  },
  integration: {
    framework: 'jest',
    setupFiles: ['./tests/setup.js'],
    testTimeout: 30000
  },
  e2e: {
    framework: 'playwright',
    baseURL: 'http://localhost:3000',
    viewport: { width: 1280, height: 720 }
  }
};
```

## Output Examples

### Test Generation Report
```
📊 Test Generation Complete
==========================

✅ Generated Tests
- Unit Tests: 45 files, 312 test cases
- Integration Tests: 12 files, 67 test cases  
- E2E Tests: 8 files, 23 scenarios

📈 Coverage Improvement
- Before: 45% line coverage
- After: 89% line coverage (+44%)
- Uncovered: 38 lines in 5 files

🎯 Critical Paths Covered
- User authentication ✓
- Payment processing ✓
- Data validation ✓
- Error handling ✓

⚡ Performance
- Test suite runtime: ~3m 20s
- Parallel execution: Enabled
- Mock optimization: Applied

📝 Next Steps
1. Review generated tests in tests/generated/
2. Run: npm test
3. Add custom assertions as needed
```

## Best Practices

1. **Incremental Generation**: Generate tests module by module
2. **Review Generated Tests**: Always review and customize
3. **Maintain Test Data**: Use factories and builders
4. **Keep Tests Fast**: Mock external dependencies
5. **Document Complex Tests**: Add comments for clarity
6. **Update Regularly**: Regenerate as code changes