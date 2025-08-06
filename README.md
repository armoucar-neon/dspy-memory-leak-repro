# DSPy Memory Leak Reproduction

Minimal reproduction of memory leaks in DSPy modules.

## Issue

DSPy modules exhibit memory leaks where memory continuously grows over time during usage, even when:
- Creating fresh instances for each use (no caching)
- Explicitly deleting instances after use  
- Forcing garbage collection

## Reproduction

```bash
# Build the image
docker build -t dspy-memory-leak .

# Test ChainOfThought module (default)
docker run --rm -e OPENAI_API_KEY='your-api-key-here' dspy-memory-leak

# Test Predict module  
docker run --rm -e OPENAI_API_KEY='your-api-key-here' -e DSPY_MODULE=predict dspy-memory-leak

# Test ChainOfThought module (explicit)
docker run --rm -e OPENAI_API_KEY='your-api-key-here' -e DSPY_MODULE=chainofthought dspy-memory-leak
```

## Expected Behavior

Memory should stabilize after initial module loading, with instances being properly garbage collected.

## Actual Behavior  

Memory continuously grows and is never released. The test demonstrates consistent memory growth over time with repeated use of DSPy modules.

This causes production issues like:
- Kubernetes pods autoscaling unnecessarily
- Increased infrastructure costs  
- Potential out-of-memory errors in long-running services

## Scope

This test supports both `ChainOfThought` and `Predict` modules. Both modules exhibit memory leaks. Additional DSPy modules can be easily added for testing.

## Environment

- Python: 3.11
- DSPy: 2.6.27
- OS: Linux (Docker python:3.11-bullseye)
- Requires: OPENAI_API_KEY environment variable