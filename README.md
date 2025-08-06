# DSPy Memory Leak Reproduction

Minimal reproduction of a memory leak in DSPy's ChainOfThought module.

## Issue

DSPy's `ChainOfThought` module exhibits a memory leak where memory continuously grows over time during usage, even when:
- Creating fresh instances for each use (no caching)
- Explicitly deleting instances after use  
- Forcing garbage collection

## Reproduction

```bash
# Build and run with your OpenAI API key
docker build -t dspy-memory-leak .
docker run --rm -e OPENAI_API_KEY='your-api-key-here' dspy-memory-leak
```

## Expected Behavior

Memory should stabilize after initial module loading, with instances being properly garbage collected.

## Actual Behavior  

Memory continuously grows and is never released. The test demonstrates consistent memory growth over time with repeated use of the ChainOfThought module.

This causes production issues like:
- Kubernetes pods autoscaling unnecessarily
- Increased infrastructure costs  
- Potential out-of-memory errors in long-running services

## Scope

This test specifically targets the `ChainOfThought` module. Other DSPy modules have not been tested yet and may exhibit similar behavior.

## Environment

- Python: 3.11
- DSPy: 2.6.27
- OS: Linux (Docker python:3.11-bullseye)
- Requires: OPENAI_API_KEY environment variable