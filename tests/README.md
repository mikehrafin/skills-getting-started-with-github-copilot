# FastAPI Test Suite

This directory contains comprehensive tests for the Mergington High School Activities FastAPI application.

## Test Structure

### `conftest.py`
- Contains pytest fixtures and configuration
- Provides test client setup
- Handles activity data reset between tests

### `test_api.py`
- **TestRootEndpoint**: Tests for the root redirect endpoint
- **TestActivitiesEndpoint**: Tests for retrieving activities
- **TestSignupEndpoint**: Tests for student registration functionality
- **TestUnregisterEndpoint**: Tests for student unregistration functionality
- **TestIntegrationScenarios**: End-to-end workflow tests
- **TestEdgeCases**: Special character and encoding tests

### `test_data_validation.py`
- **TestDataValidation**: Data integrity and constraint tests
- **TestActivityData**: Activity structure and format validation
- **TestConcurrency**: Concurrent operation tests
- **TestErrorHandling**: Error scenarios and edge cases

### `test_performance.py`
- **TestPerformance**: Basic response time and performance tests
- **TestLoad**: Bulk operations and load testing
- **TestMemoryUsage**: Memory stability and large dataset tests

## Running Tests

### Basic Usage

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_api.py

# Run specific test class
python -m pytest tests/test_api.py::TestSignupEndpoint

# Run specific test method
python -m pytest tests/test_api.py::TestSignupEndpoint::test_signup_success
```

### Using the Test Runner Script

```bash
# Basic test run
python run_tests.py

# Verbose output
python run_tests.py --verbose

# Skip slow tests
python run_tests.py --fast

# Run specific file
python run_tests.py --file test_api.py

# Run specific test
python run_tests.py --test signup

# Run with coverage report
python run_tests.py --coverage
```

## Test Categories

### Unit Tests
- Individual endpoint functionality
- Data validation
- Error handling

### Integration Tests
- Complete user workflows
- Multi-step operations
- Data persistence across operations

### Performance Tests
- Response time validation
- Bulk operation handling
- Memory usage stability

## Coverage

The tests cover:
- ✅ All API endpoints (`/`, `/activities`, `/activities/{name}/signup`, `/activities/{name}/unregister`)
- ✅ Success and error cases
- ✅ Data validation and integrity
- ✅ Edge cases and special characters
- ✅ Concurrent operations
- ✅ Performance characteristics

## Dependencies

Required packages (automatically installed):
- `pytest` - Testing framework
- `httpx` - HTTP client for FastAPI testing
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting (optional)

## Configuration

Test configuration is managed through:
- `pytest.ini` - Pytest settings and markers
- `conftest.py` - Fixtures and test setup
- Environment-specific settings handled automatically

## Continuous Integration

These tests are designed to run in CI/CD pipelines and will:
- Exit with appropriate status codes
- Provide detailed failure information
- Support coverage reporting
- Handle concurrent test execution