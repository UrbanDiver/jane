# Improvements Quick Reference

**Quick guide for implementing improvements**

---

## Starting a New Step

1. **Check Status**
   ```bash
   # Review current status
   cat IMPROVEMENTS_STATUS.md
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/phase-X-step-Y-description
   # Example: feature/phase-1-step-1-config-system
   ```

3. **Review Step Details**
   - Open `IMPROVEMENTS_IMPLEMENTATION_PLAN.md`
   - Find the step you're working on
   - Review objectives, implementation details, and testing criteria

4. **Implement**
   - Follow the implementation details
   - Write code
   - Add tests as you go

5. **Test**
   ```bash
   # Run specific test
   python test_<step_name>.py
   
   # Run all tests
   pytest
   ```

6. **Update Status**
   - Update `IMPROVEMENTS_STATUS.md`
   - Mark step as "In Progress" when starting
   - Mark as "Completed" when done
   - Add commit hash

7. **Commit**
   ```bash
   git add .
   git commit -m "feat: <step description>

   - <change 1>
   - <change 2>
   - <change 3>"
   ```

8. **Verify**
   - All tests pass
   - Code follows style guidelines
   - Documentation updated
   - Status document updated

---

## Step Status Values

- ⏳ **Pending** - Not started
- 🔄 **In Progress** - Currently working on
- ✅ **Completed** - Done and tested
- ⚠️ **Blocked** - Cannot proceed (add note)
- ❌ **Failed** - Tests failed (add note)

---

## Commit Message Template

```
<type>: <short description>

<detailed description of changes>

- <change 1>
- <change 2>
- <change 3>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `perf`: Performance improvement
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `docs`: Documentation changes
- `chore`: Maintenance tasks

### Examples

```
feat: Add configuration system with YAML support

- Add Pydantic-based config schema
- Support YAML config files
- Environment variable overrides
- Configuration validation
- Update all components to use config
```

```
perf: Optimize STT engine for lower latency

- Add quantization support
- Implement chunked processing
- Add model caching
- Optimize audio preprocessing
```

---

## Testing Checklist

Before marking a step as complete:

- [ ] All unit tests pass
- [ ] Integration tests pass (if applicable)
- [ ] Code coverage maintained/improved
- [ ] No linting errors
- [ ] Documentation updated
- [ ] Status document updated
- [ ] Commit made with proper message

---

## Common Commands

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest test_config_system.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest test_config_system.py::test_config_loading
```

### Code Quality
```bash
# Format code
black src/

# Lint
flake8 src/
pylint src/

# Type check
mypy src/
```

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/phase-X-step-Y

# Commit changes
git add .
git commit -m "feat: ..."

# Push branch
git push origin feature/phase-X-step-Y

# Merge to main (after review)
git checkout main
git merge feature/phase-X-step-Y
```

---

## Phase Overview

### Phase 1: Foundation (3 steps)
- Config system
- Logging
- Error handling

### Phase 2: Performance (4 steps)
- Context management
- Streaming
- Memory management
- STT optimizations

### Phase 3: Functionality (3 steps)
- Function calling
- Context management
- New functions

### Phase 4: Extensibility (3 steps)
- Interfaces
- Plugins
- Dependency injection

### Phase 5: Advanced (2 steps)
- Wake word
- API (optional)

---

## Getting Help

1. **Review Implementation Plan**
   - Detailed step-by-step instructions
   - Testing criteria
   - Expected outcomes

2. **Check Status Document**
   - Current progress
   - Blockers
   - Recent activity

3. **Review Existing Code**
   - Similar implementations
   - Patterns to follow
   - Test examples

4. **Document Issues**
   - Add to status document
   - Note blockers
   - Document workarounds

---

## Status Update Template

When updating `IMPROVEMENTS_STATUS.md`:

```markdown
### Step X.Y: Description
- **Status:** ✅ Completed (or 🔄 In Progress)
- **Started:** 2025-11-30
- **Completed:** 2025-11-30
- **Tests:** ✅ All Pass
- **Commit:** abc1234 - "feat: ..."
- **Notes:** Any important notes or issues encountered
```

---

## Quick Links

- **Implementation Plan:** `IMPROVEMENTS_IMPLEMENTATION_PLAN.md`
- **Status Tracking:** `IMPROVEMENTS_STATUS.md`
- **This Reference:** `IMPROVEMENTS_QUICK_REFERENCE.md`
- **Main Status:** `WHERE_WE_LEFT_OFF.md`

---

**Last Updated:** 2025-11-30

