# Function Calling Performance Optimization Plan

**Date:** 2025-12-01  
**Current Performance:** 45+ seconds for function calling  
**Target:** <5 seconds for function calling  
**Gap:** 9x improvement needed

---

## 🔍 Current Performance Analysis

### Logs Show:
- Function calling: **45.215s** (still very slow!)
- Regular responses: **19.106s** (after function execution)
- Total: **~64s** end-to-end

### Root Causes:
1. **Model size:** Using 7B model (hardcoded in jane.py)
2. **Function definitions:** Full JSON schema sent to LLM (~159 tokens)
3. **Context processing:** LLM must process all function definitions
4. **No early stopping:** LLM generates full response even after function call detected
5. **No pattern matching:** All queries go through LLM, even simple ones

---

## 🚀 Optimization Strategies

### Strategy 1: Pattern Matching for Common Functions ⚡ (Highest Impact)

**Idea:** Use pattern matching for simple, common functions (time, date) to bypass LLM entirely.

**Implementation:**
- Detect common patterns: "what time", "what date", "current time", etc.
- Execute function directly without LLM call
- Only use LLM function calling for complex queries

**Expected Improvement:** 45s → **<1s** for time/date queries (90-95% faster)

**Trade-off:** Less flexible, but much faster for common cases

---

### Strategy 2: Optimize Function Definitions 📝

**Idea:** Reduce the size of function definitions sent to LLM.

**Current:**
```json
{
  "type": "function",
  "function": {
    "name": "get_current_time",
    "description": "Get the current time in 12-hour format (e.g., '3:45 PM')",
    "parameters": {
      "type": "object",
      "properties": {},
      "required": []
    }
  }
}
```

**Optimized:**
```json
{
  "type": "function",
  "function": {
    "name": "get_current_time",
    "description": "Get current time",
    "parameters": {"type": "object", "properties": {}, "required": []}
  }
}
```

**Expected Improvement:** 10-20% faster (reduces context size)

---

### Strategy 3: Stop Sequences for Function Calls 🛑

**Idea:** Add stop sequences to stop generation immediately after function call is detected.

**Implementation:**
- Add `stop=["</tool_call>"]` when function calling is enabled
- Stop generation as soon as function call tag is complete
- Prevents unnecessary token generation

**Expected Improvement:** 20-30% faster (stops generation early)

---

### Strategy 4: Two-Stage Approach 🔄

**Idea:** Quick check first, then function calling only if needed.

**Implementation:**
1. First call: Simple prompt without function definitions (fast check)
2. If response suggests function needed, second call with functions
3. Most queries won't need second call

**Expected Improvement:** 30-50% faster for non-function queries

**Trade-off:** Adds overhead for function queries (but still faster overall)

---

### Strategy 5: Use Smaller Model 🎯

**Idea:** Switch to 3B model (already in config.yaml, but jane.py overrides it).

**Current:** 7B Q4_K_M (hardcoded in jane.py)  
**Target:** 3B Q5_K_M (in config.yaml)

**Expected Improvement:** 2-3x faster (smaller model = faster inference)

**Implementation:** Update jane.py to use config.yaml model path

---

### Strategy 6: Reduce Context for Function Calling 📉

**Idea:** Use smaller context window specifically for function calling.

**Current:** 2048 tokens  
**Proposed:** 1024 tokens for function calling (if possible)

**Expected Improvement:** 10-15% faster

**Note:** Already tried 1024, but function definitions exceeded it. Could work with optimized definitions.

---

### Strategy 7: Parallel Function Execution ⚡

**Idea:** If multiple functions are called, execute them in parallel.

**Current:** Sequential execution  
**Proposed:** Parallel execution with threading

**Expected Improvement:** 50% faster for multi-function calls

**Note:** Only helps if multiple functions are called

---

## 📊 Recommended Implementation Order

### Phase 1: Quick Wins (Immediate)
1. ✅ **Pattern Matching** - Bypass LLM for common functions
2. ✅ **Stop Sequences** - Stop generation early
3. ✅ **Optimize Function Definitions** - Shorter descriptions

**Expected:** 45s → **~5-10s** (80-90% improvement)

### Phase 2: Model & Config (Medium-term)
4. ✅ **Use 3B Model** - Update jane.py to use config.yaml
5. ✅ **Reduce Context** - If optimized definitions allow

**Expected:** 5-10s → **~3-5s** (additional 50% improvement)

### Phase 3: Advanced (Long-term)
6. ✅ **Two-Stage Approach** - If still needed
7. ✅ **Parallel Execution** - For multi-function calls

**Expected:** 3-5s → **~2-3s** (final optimization)

---

## 🎯 Target Performance

| Query Type | Current | Target | Strategy |
|------------|---------|--------|----------|
| **Time/Date** | 45s | **<1s** | Pattern matching |
| **Simple Functions** | 45s | **~3-5s** | Optimizations 1-5 |
| **Complex Functions** | 45s | **~5-8s** | Optimizations 1-5 |

---

## 💡 Implementation Priority

**High Priority (Do First):**
1. Pattern matching for time/date functions
2. Stop sequences for function calls
3. Use 3B model from config

**Medium Priority:**
4. Optimize function definitions
5. Reduce context if possible

**Low Priority (If Still Needed):**
6. Two-stage approach
7. Parallel execution

---

## 📝 Notes

- Pattern matching is the biggest win (90%+ improvement for common queries)
- Stop sequences are easy to implement and provide immediate benefit
- Using 3B model requires updating jane.py (currently hardcoded)
- Function definition optimization is low-risk, easy to implement

---

**Next Steps:** Implement Phase 1 optimizations for immediate impact.

