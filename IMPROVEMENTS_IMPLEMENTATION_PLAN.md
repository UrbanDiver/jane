# Improvements Implementation Plan

**Created:** 2025-11-30  
**Status:** 🚀 Ready to Begin  
**Total Phases:** 5  
**Estimated Duration:** 2-3 weeks (depending on complexity)

---

## Overview

This document outlines a detailed, step-by-step plan for implementing performance, functionality, and extensibility improvements to the Jane AI Voice Assistant. Each step includes:

- **Clear objectives**
- **Implementation details**
- **Testing criteria**
- **Commit checkpoints**
- **Status tracking**

---

## Phase 1: Foundation & Infrastructure (Priority: HIGH)

**Goal:** Establish solid foundation for future improvements  
**Estimated Time:** 3-4 days  
**Dependencies:** None

### Step 1.1: Configuration System
**Status:** ⏳ Pending  
**Estimated Time:** 4-6 hours

#### Objectives
- Create YAML/JSON configuration system
- Support environment variable overrides
- Validate configuration on load
- Provide sensible defaults

#### Implementation Details
1. Create `src/config/` directory
2. Create `config_schema.py` with Pydantic models:
   - `STTConfig`
   - `TTSConfig`
   - `LLMConfig`
   - `AssistantConfig`
   - `FileControllerConfig`
   - `AppControllerConfig`
   - `InputControllerConfig`
3. Create `config_loader.py`:
   - Load from `config.yaml` (if exists)
   - Override with environment variables
   - Validate against schema
   - Return typed config objects
4. Create default `config.yaml` template
5. Update `assistant_core.py` to use config
6. Update all engine/controller init methods to accept config

#### Files to Create/Modify
- `src/config/__init__.py` (new)
- `src/config/config_schema.py` (new)
- `src/config/config_loader.py` (new)
- `config.yaml` (new - template)
- `config.yaml.example` (new - example)
- `src/backend/assistant_core.py` (modify)
- `src/backend/stt_engine.py` (modify)
- `src/backend/tts_engine.py` (modify)
- `src/backend/llm_engine.py` (modify)
- `src/backend/file_controller.py` (modify)
- `src/backend/app_controller.py` (modify)
- `src/backend/input_controller.py` (modify)

#### Testing Criteria
- [ ] Config loads from YAML file
- [ ] Environment variables override YAML values
- [ ] Invalid config raises clear error messages
- [ ] Default config works if no file exists
- [ ] All components initialize with config
- [ ] Type validation works correctly

#### Test Script
Create `test_config_system.py`:
```python
# Test config loading
# Test environment variable overrides
# Test validation
# Test defaults
```

#### Commit Message
```
feat: Add configuration system with YAML and environment variable support

- Add Pydantic-based config schema
- Support YAML config files
- Environment variable overrides
- Configuration validation
- Update all components to use config
```

---

### Step 1.2: Logging System
**Status:** ⏳ Pending  
**Estimated Time:** 3-4 hours

#### Objectives
- Implement structured logging throughout codebase
- Support different log levels
- Log to file and console
- Include performance metrics

#### Implementation Details
1. Create `src/utils/logger.py`:
   - Configure logging with levels (DEBUG, INFO, WARNING, ERROR)
   - File handler (rotating logs)
   - Console handler with colors
   - Performance timing decorators
2. Add logging to all modules:
   - `assistant_core.py`
   - `stt_engine.py`
   - `tts_engine.py`
   - `llm_engine.py`
   - `function_handler.py`
   - All controllers
3. Add performance logging:
   - STT transcription time
   - TTS synthesis time
   - LLM generation time
   - Function execution time
4. Create log rotation (keep last 7 days)

#### Files to Create/Modify
- `src/utils/__init__.py` (new)
- `src/utils/logger.py` (new)
- All backend modules (add logging)
- `requirements.txt` (add `colorlog` if needed)

#### Testing Criteria
- [ ] Logs appear in console with appropriate levels
- [ ] Logs written to file
- [ ] Performance metrics logged correctly
- [ ] Log rotation works
- [ ] Different log levels filter correctly

#### Test Script
Create `test_logging.py`:
```python
# Test log levels
# Test file logging
# Test performance logging
# Test log rotation
```

#### Commit Message
```
feat: Add structured logging system with performance metrics

- Implement centralized logger with file and console handlers
- Add performance timing for all major operations
- Add logging throughout codebase
- Support log rotation
```

---

### Step 1.3: Error Handling & Recovery
**Status:** ⏳ Pending  
**Estimated Time:** 4-5 hours

#### Objectives
- Implement retry logic for transient failures
- Add graceful degradation
- Improve error messages
- Add error recovery mechanisms

#### Implementation Details
1. Create `src/utils/retry.py`:
   - Retry decorator with exponential backoff
   - Configurable max retries
   - Exception filtering
2. Create `src/utils/error_handler.py`:
   - Error classification (transient vs permanent)
   - Error recovery strategies
   - Fallback mechanisms
3. Add retry logic to:
   - STT transcription
   - LLM generation
   - Function execution
4. Add fallback mechanisms:
   - CPU fallback if GPU unavailable
   - Smaller model fallback if large model fails
   - Simplified processing on errors
5. Improve error messages with context

#### Files to Create/Modify
- `src/utils/retry.py` (new)
- `src/utils/error_handler.py` (new)
- `src/backend/stt_engine.py` (add retry)
- `src/backend/llm_engine.py` (add retry + fallback)
- `src/backend/assistant_core.py` (add error handling)

#### Testing Criteria
- [ ] Retry logic works for transient failures
- [ ] Permanent failures fail fast
- [ ] Fallback mechanisms activate correctly
- [ ] Error messages are clear and actionable
- [ ] System recovers gracefully from errors

#### Test Script
Create `test_error_handling.py`:
```python
# Test retry logic
# Test fallback mechanisms
# Test error classification
# Test error recovery
```

#### Commit Message
```
feat: Add comprehensive error handling and recovery system

- Implement retry logic with exponential backoff
- Add graceful degradation and fallback mechanisms
- Improve error messages with context
- Add error classification and recovery strategies
```

---

## Phase 2: Performance Optimizations (Priority: HIGH)

**Goal:** Improve response times and resource efficiency  
**Estimated Time:** 4-5 days  
**Dependencies:** Phase 1 complete

### Step 2.1: Context Window Management
**Status:** ⏳ Pending  
**Estimated Time:** 5-6 hours

#### Objectives
- Prevent conversation history from growing unbounded
- Implement smart context pruning
- Add conversation summarization
- Maintain important context

#### Implementation Details
1. Create `src/backend/context_manager.py`:
   - `ContextManager` class
   - Conversation history pruning
   - Context summarization (using LLM)
   - Important message retention
2. Implement sliding window:
   - Keep last N messages
   - Keep system message
   - Keep important messages (function results, etc.)
3. Add summarization:
   - Summarize old messages when context gets long
   - Inject summary as system message
4. Update `assistant_core.py` to use context manager

#### Files to Create/Modify
- `src/backend/context_manager.py` (new)
- `src/backend/assistant_core.py` (modify)

#### Testing Criteria
- [ ] Context window limits conversation history
- [ ] Important messages are retained
- [ ] Summarization works correctly
- [ ] System message always present
- [ ] Performance doesn't degrade with long conversations

#### Test Script
Create `test_context_management.py`:
```python
# Test context pruning
# Test summarization
# Test important message retention
# Test performance with long conversations
```

#### Commit Message
```
feat: Add context window management with smart pruning

- Implement sliding window for conversation history
- Add conversation summarization
- Retain important messages
- Prevent unbounded memory growth
```

---

### Step 2.2: Streaming Responses
**Status:** ⏳ Pending  
**Estimated Time:** 4-5 hours

#### Objectives
- Stream LLM responses for faster perceived latency
- Start TTS synthesis as soon as first tokens arrive
- Improve user experience with progressive responses

#### Implementation Details
1. Update `assistant_core.py`:
   - Use `llm.stream_chat()` instead of `llm.chat()`
   - Buffer tokens until sentence boundaries
   - Start TTS synthesis early
   - Handle streaming errors gracefully
2. Add sentence boundary detection:
   - Buffer tokens until complete sentence
   - Speak complete sentences
3. Update voice loop to handle streaming
4. Add visual feedback (optional: print tokens as they arrive)

#### Files to Create/Modify
- `src/backend/assistant_core.py` (modify)
- `src/utils/sentence_splitter.py` (new - optional)

#### Testing Criteria
- [ ] Responses stream correctly
- [ ] TTS starts before full response
- [ ] Sentence boundaries detected correctly
- [ ] Error handling works during streaming
- [ ] Perceived latency is reduced

#### Test Script
Create `test_streaming.py`:
```python
# Test streaming responses
# Test sentence boundary detection
# Test early TTS start
# Test error handling during streaming
```

#### Commit Message
```
feat: Implement streaming responses for reduced latency

- Stream LLM responses token-by-token
- Start TTS synthesis early
- Detect sentence boundaries
- Improve perceived response time
```

---

### Step 2.3: Memory Management
**Status:** ⏳ Pending  
**Estimated Time:** 3-4 hours

#### Objectives
- Clean up temporary files properly
- Manage GPU memory efficiently
- Monitor memory usage
- Prevent memory leaks

#### Implementation Details
1. Create `src/utils/memory_manager.py`:
   - Temporary file cleanup
   - GPU memory monitoring
   - Memory leak detection
2. Use context managers for temp files:
   - Update `streaming_stt.py`
   - Update `tts_engine.py`
3. Add GPU memory cleanup:
   - Clear cache after large operations
   - Monitor VRAM usage
4. Add memory usage logging

#### Files to Create/Modify
- `src/utils/memory_manager.py` (new)
- `src/backend/streaming_stt.py` (modify)
- `src/backend/tts_engine.py` (modify)
- `src/backend/stt_engine.py` (modify)

#### Testing Criteria
- [ ] Temporary files are cleaned up
- [ ] GPU memory is monitored
- [ ] No memory leaks over time
- [ ] Memory usage logged correctly

#### Test Script
Create `test_memory_management.py`:
```python
# Test temp file cleanup
# Test GPU memory monitoring
# Test for memory leaks
# Test memory usage logging
```

#### Commit Message
```
feat: Add comprehensive memory management

- Implement temporary file cleanup
- Add GPU memory monitoring
- Prevent memory leaks
- Add memory usage logging
```

---

### Step 2.4: STT Optimizations
**Status:** ⏳ Pending  
**Estimated Time:** 5-6 hours

#### Objectives
- Reduce STT latency
- Optimize model loading
- Add quantization options
- Improve streaming transcription

#### Implementation Details
1. Add model quantization options:
   - Support `int8` and `int8_float16` compute types
   - Auto-select based on GPU memory
2. Implement chunked processing:
   - Process audio in overlapping chunks
   - Reduce latency for long audio
3. Add model caching:
   - Keep model in memory between sessions
   - Lazy loading option
4. Optimize audio preprocessing:
   - Efficient audio format conversion
   - Reduce unnecessary copies

#### Files to Create/Modify
- `src/backend/stt_engine.py` (modify)
- `src/backend/streaming_stt.py` (modify)

#### Testing Criteria
- [ ] Quantization reduces memory usage
- [ ] Chunked processing reduces latency
- [ ] Model caching works
- [ ] Performance improved

#### Test Script
Create `test_stt_optimizations.py`:
```python
# Test quantization
# Test chunked processing
# Test model caching
# Benchmark performance improvements
```

#### Commit Message
```
perf: Optimize STT engine for lower latency

- Add quantization support
- Implement chunked processing
- Add model caching
- Optimize audio preprocessing
```

---

## Phase 3: Functionality Enhancements (Priority: HIGH)

**Goal:** Add critical missing features  
**Estimated Time:** 5-6 days  
**Dependencies:** Phase 1 complete

### Step 3.1: LLM Function Calling Integration
**Status:** ⏳ Pending  
**Estimated Time:** 6-8 hours

#### Objectives
- Replace pattern matching with native LLM function calling
- Support automatic function selection
- Handle function results properly
- Support multi-step function chains

#### Implementation Details
1. Update `llm_engine.py`:
   - Add function calling support to `chat()` method
   - Format function definitions for LLM
   - Parse function calls from LLM response
2. Update `assistant_core.py`:
   - Remove pattern matching (`_try_function_call`)
   - Use LLM function calling
   - Execute functions based on LLM decisions
   - Inject function results back into conversation
3. Support multi-step chains:
   - Allow LLM to call multiple functions
   - Handle function dependencies
4. Add function calling tests

#### Files to Create/Modify
- `src/backend/llm_engine.py` (modify)
- `src/backend/assistant_core.py` (modify - major refactor)
- `src/backend/function_handler.py` (enhance)

#### Testing Criteria
- [ ] LLM correctly identifies when to call functions
- [ ] Functions are executed with correct parameters
- [ ] Function results are injected into conversation
- [ ] Multi-step function chains work
- [ ] Falls back gracefully when function calling unavailable

#### Test Script
Create `test_function_calling.py`:
```python
# Test function detection
# Test function execution
# Test result injection
# Test multi-step chains
# Test error handling
```

#### Commit Message
```
feat: Implement native LLM function calling

- Replace pattern matching with LLM-driven function calling
- Support automatic function selection
- Handle function results in conversation
- Support multi-step function chains
```

---

### Step 3.2: Conversation Context Management
**Status:** ⏳ Pending  
**Estimated Time:** 4-5 hours

#### Objectives
- Track conversation topics
- Remember user preferences
- Maintain conversation state
- Support conversation resumption

#### Implementation Details
1. Enhance `context_manager.py`:
   - Topic extraction
   - Preference tracking
   - State management
2. Create `src/backend/conversation_state.py`:
   - Conversation state class
   - Topic tracking
   - Preference storage
3. Add persistence:
   - Save conversation state to file
   - Load state on startup
4. Update `assistant_core.py` to use state

#### Files to Create/Modify
- `src/backend/conversation_state.py` (new)
- `src/backend/context_manager.py` (enhance)
- `src/backend/assistant_core.py` (modify)

#### Testing Criteria
- [ ] Topics are tracked correctly
- [ ] Preferences are remembered
- [ ] State persists across sessions
- [ ] Conversation can be resumed

#### Test Script
Create `test_conversation_state.py`:
```python
# Test topic tracking
# Test preference storage
# Test state persistence
# Test conversation resumption
```

#### Commit Message
```
feat: Add conversation context and state management

- Track conversation topics
- Remember user preferences
- Persist conversation state
- Support conversation resumption
```

---

### Step 3.3: Additional Functions
**Status:** ⏳ Pending  
**Estimated Time:** 6-8 hours

#### Objectives
- Add web search capability
- Add system information functions
- Add calendar/email functions (optional)
- Make function registration easier

#### Implementation Details
1. Create `src/backend/web_search.py`:
   - Web search function using DuckDuckGo or similar
   - Parse and format results
2. Create `src/backend/system_info.py`:
   - Get system stats
   - Get network info
   - Get disk usage
3. Register new functions:
   - `search_web(query)`
   - `get_system_info()`
   - `get_network_info()`
   - `get_disk_usage()`
4. Update function handler to make registration easier

#### Files to Create/Modify
- `src/backend/web_search.py` (new)
- `src/backend/system_info.py` (new)
- `src/backend/assistant_core.py` (register functions)
- `requirements.txt` (add web search library)

#### Testing Criteria
- [ ] Web search returns relevant results
- [ ] System info functions work correctly
- [ ] All functions are registered
- [ ] Functions can be called via LLM

#### Test Script
Create `test_new_functions.py`:
```python
# Test web search
# Test system info functions
# Test function registration
# Test LLM function calling
```

#### Commit Message
```
feat: Add web search and system information functions

- Implement web search capability
- Add system information functions
- Simplify function registration
- Register new functions with assistant
```

---

## Phase 4: Extensibility Improvements (Priority: MEDIUM)

**Goal:** Make system easier to extend  
**Estimated Time:** 4-5 days  
**Dependencies:** Phase 1-2 complete

### Step 4.1: Abstract Base Classes
**Status:** ⏳ Pending  
**Estimated Time:** 3-4 hours

#### Objectives
- Define interfaces for all engines
- Make components swappable
- Improve testability
- Document expected interfaces

#### Implementation Details
1. Create `src/interfaces/` directory
2. Create interface classes:
   - `STTEngineInterface`
   - `TTSEngineInterface`
   - `LLMEngineInterface`
   - `FunctionHandlerInterface`
   - `ControllerInterface`
3. Update existing classes to implement interfaces
4. Add type hints throughout

#### Files to Create/Modify
- `src/interfaces/__init__.py` (new)
- `src/interfaces/engines.py` (new)
- `src/interfaces/controllers.py` (new)
- All engine classes (modify to implement interfaces)

#### Testing Criteria
- [ ] All interfaces are properly defined
- [ ] Existing classes implement interfaces
- [ ] Type checking passes
- [ ] Interfaces are documented

#### Test Script
Create `test_interfaces.py`:
```python
# Test interface definitions
# Test implementation compliance
# Test type checking
```

#### Commit Message
```
refactor: Add abstract base classes for all components

- Define interfaces for engines and controllers
- Make components swappable
- Improve type safety
- Document expected interfaces
```

---

### Step 4.2: Plugin System
**Status:** ⏳ Pending  
**Estimated Time:** 6-8 hours

#### Objectives
- Create plugin architecture
- Allow third-party plugins
- Support function registration from plugins
- Add plugin hooks/events

#### Implementation Details
1. Create `src/plugins/` directory
2. Create `plugin_manager.py`:
   - Plugin discovery
   - Plugin loading
   - Plugin lifecycle management
3. Create `plugin_base.py`:
   - Base plugin class
   - Hook system
   - Function registration
4. Create example plugin
5. Update `assistant_core.py` to support plugins

#### Files to Create/Modify
- `src/plugins/__init__.py` (new)
- `src/plugins/plugin_base.py` (new)
- `src/plugins/plugin_manager.py` (new)
- `src/plugins/example_plugin.py` (new - example)
- `src/backend/assistant_core.py` (modify)

#### Testing Criteria
- [ ] Plugins can be loaded
- [ ] Plugins can register functions
- [ ] Plugin hooks work
- [ ] Example plugin works

#### Test Script
Create `test_plugin_system.py`:
```python
# Test plugin loading
# Test function registration
# Test hooks
# Test example plugin
```

#### Commit Message
```
feat: Add plugin system for extensibility

- Implement plugin architecture
- Support third-party plugins
- Add hook system
- Create example plugin
```

---

### Step 4.3: Dependency Injection
**Status:** ⏳ Pending  
**Estimated Time:** 3-4 hours

#### Objectives
- Refactor to use dependency injection
- Improve testability
- Reduce coupling
- Make components swappable

#### Implementation Details
1. Update `assistant_core.py`:
   - Accept dependencies in constructor
   - Make all dependencies optional with defaults
2. Create factory functions for component creation
3. Update initialization to use DI
4. Add tests with mocked dependencies

#### Files to Create/Modify
- `src/backend/assistant_core.py` (refactor)
- `src/utils/factories.py` (new - optional)

#### Testing Criteria
- [ ] Components can be injected
- [ ] Defaults work when not provided
- [ ] Mocking works for tests
- [ ] Components are decoupled

#### Test Script
Update existing tests to use DI:
```python
# Test with injected dependencies
# Test with mocked dependencies
# Test default behavior
```

#### Commit Message
```
refactor: Implement dependency injection pattern

- Refactor AssistantCore to accept dependencies
- Improve testability with DI
- Reduce component coupling
- Add factory functions
```

---

## Phase 5: Advanced Features (Priority: MEDIUM-LOW)

**Goal:** Add advanced capabilities  
**Estimated Time:** 5-6 days  
**Dependencies:** Phase 1-3 complete

### Step 5.1: Wake Word Detection
**Status:** ⏳ Pending  
**Estimated Time:** 6-8 hours

#### Objectives
- Add wake word detection
- Only run full STT after wake word
- Energy efficient listening
- Configurable wake word

#### Implementation Details
1. Research wake word libraries (Porcupine, etc.)
2. Create `src/backend/wake_word_detector.py`:
   - Wake word detection
   - Continuous listening
   - Wake word trigger
3. Integrate with `assistant_core.py`:
   - Listen for wake word
   - Activate full STT after detection
4. Add configuration for wake word

#### Files to Create/Modify
- `src/backend/wake_word_detector.py` (new)
- `src/backend/assistant_core.py` (modify)
- `config.yaml` (add wake word config)
- `requirements.txt` (add wake word library)

#### Testing Criteria
- [ ] Wake word is detected correctly
- [ ] Full STT activates after wake word
- [ ] Energy usage is reduced
- [ ] Configurable wake word works

#### Test Script
Create `test_wake_word.py`:
```python
# Test wake word detection
# Test activation
# Test energy efficiency
```

#### Commit Message
```
feat: Add wake word detection for energy-efficient listening

- Implement wake word detection
- Activate full STT only after wake word
- Reduce energy consumption
- Support configurable wake words
```

---

### Step 5.2: API Layer (Optional)
**Status:** ⏳ Pending  
**Estimated Time:** 8-10 hours

#### Objectives
- Expose functionality via REST API
- Support WebSocket for real-time
- Add authentication
- Document API

#### Implementation Details
1. Create `src/api/` directory
2. Create FastAPI application:
   - REST endpoints
   - WebSocket endpoint
   - Authentication
3. Add API documentation
4. Create API client example

#### Files to Create/Modify
- `src/api/__init__.py` (new)
- `src/api/main.py` (new)
- `src/api/routes.py` (new)
- `src/api/websocket.py` (new)
- `requirements.txt` (add FastAPI, uvicorn)

#### Testing Criteria
- [ ] REST API works
- [ ] WebSocket works
- [ ] Authentication works
- [ ] API is documented

#### Test Script
Create `test_api.py`:
```python
# Test REST endpoints
# Test WebSocket
# Test authentication
```

#### Commit Message
```
feat: Add REST API and WebSocket support

- Implement FastAPI REST API
- Add WebSocket for real-time communication
- Add authentication
- Document API endpoints
```

---

## Testing Strategy

### Unit Tests
- Each module should have comprehensive unit tests
- Test all public methods
- Test error cases
- Test edge cases

### Integration Tests
- Test component interactions
- Test end-to-end workflows
- Test error recovery
- Test performance

### Test Coverage Goals
- Minimum 80% code coverage
- 100% coverage for critical paths
- All new code must have tests

### Continuous Testing
- Run tests before each commit
- Run full test suite after each phase
- Use pytest for test execution

---

## Commit Strategy

### Commit Frequency
- Commit after each completed step
- Commit after passing tests
- Commit working code only

### Commit Message Format
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `perf`: Performance improvement
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `docs`: Documentation changes
- `chore`: Maintenance tasks

### Branch Strategy
- Create feature branch for each phase: `feature/phase-1-foundation`
- Merge to main after phase completion
- Tag releases: `v1.1.0`, `v1.2.0`, etc.

---

## Status Tracking

### Status Document
Maintain `IMPROVEMENTS_STATUS.md` with:
- Current phase and step
- Completed steps
- In-progress steps
- Blockers/issues
- Next steps

### Update Frequency
- Update status after each step completion
- Update status when blockers occur
- Update status daily during active development

---

## Risk Management

### Potential Risks
1. **Complexity**: Some features may be more complex than estimated
   - **Mitigation**: Break into smaller steps, adjust timeline

2. **Breaking Changes**: Changes may break existing functionality
   - **Mitigation**: Comprehensive testing, gradual rollout

3. **Performance Regressions**: Optimizations may not work as expected
   - **Mitigation**: Benchmark before/after, rollback capability

4. **Dependency Issues**: New dependencies may conflict
   - **Mitigation**: Test in isolated environment, pin versions

### Rollback Plan
- Keep working version in separate branch
- Tag stable versions
- Maintain changelog

---

## Success Criteria

### Phase 1 Success
- [ ] Configuration system works
- [ ] Logging is comprehensive
- [ ] Error handling is robust
- [ ] All tests pass

### Phase 2 Success
- [ ] Performance improved by 20%+
- [ ] Memory usage is stable
- [ ] Latency reduced
- [ ] All tests pass

### Phase 3 Success
- [ ] Function calling works
- [ ] New functions are available
- [ ] Context management works
- [ ] All tests pass

### Phase 4 Success
- [ ] Plugin system works
- [ ] Components are swappable
- [ ] Code is more maintainable
- [ ] All tests pass

### Phase 5 Success
- [ ] Wake word detection works
- [ ] API is functional (if implemented)
- [ ] All features work together
- [ ] All tests pass

---

## Timeline

### Week 1
- **Days 1-2**: Phase 1 (Foundation)
- **Days 3-4**: Phase 2 (Performance - Part 1)
- **Day 5**: Testing and bug fixes

### Week 2
- **Days 1-2**: Phase 2 (Performance - Part 2)
- **Days 3-4**: Phase 3 (Functionality)
- **Day 5**: Testing and bug fixes

### Week 3
- **Days 1-2**: Phase 4 (Extensibility)
- **Days 3-4**: Phase 5 (Advanced Features)
- **Day 5**: Final testing, documentation, release

---

## Notes

- Adjust timeline based on actual progress
- Some steps can be done in parallel
- Focus on high-priority items first
- Don't skip testing
- Document as you go
- Keep status document updated

---

**Last Updated:** 2025-11-30  
**Next Review:** After Phase 1 completion

