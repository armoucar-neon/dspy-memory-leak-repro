#!/usr/bin/env python3
"""
Minimal reproduction of DSPy memory leak issue.
Each iteration creates a fresh ChainOfThought instance and deletes it,
but memory continuously grows and is never released.
"""

import gc
import asyncio
import os
from datetime import datetime
import dspy


def get_memory():
    """Get memory info from /proc/self/status (Linux only)."""
    memory_info = {}
    with open("/proc/self/status", "r") as f:
        for line in f:
            if line.startswith("VmRSS"):
                memory_info["rss_mb"] = int(line.split()[1]) / 1024
            elif line.startswith("VmSize"):
                memory_info["vms_mb"] = int(line.split()[1]) / 1024
            elif line.startswith("VmData"):
                memory_info["data_mb"] = int(line.split()[1]) / 1024
    return memory_info


# Define signature outside of function to avoid recreation
class SimpleSignature(dspy.Signature):
    """Simple test signature."""

    context: str = dspy.InputField(desc="Context information")
    query: str = dspy.InputField(desc="Query to process")
    result: str = dspy.OutputField(desc="Processed result")


async def test_iteration(num_parallel_calls=10):
    """Test DSPy ChainOfThought with parallel calls."""
    
    # Get API key for this iteration
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # Use context manager to create localized LM instance
    with dspy.context(lm=dspy.LM("openai/gpt-3.5-turbo", api_key=api_key, cache=False)):
        # Get module type from environment variable
        module_type = os.environ.get("DSPY_MODULE", "chainofthought")

        # Create fresh module instance
        if module_type == "predict":
            module = dspy.Predict(SimpleSignature)
        else:  # default to chainofthought
            module = dspy.ChainOfThought(SimpleSignature)

        # Create test inputs
        test_inputs = []
        for i in range(num_parallel_calls):
            test_inputs.append((f"Context for request {i}", f"Query number {i}"))

        # Execute parallel calls
        coroutines = []
        for context, query in test_inputs:
            coro = module.acall(context=context, query=query)
            coroutines.append(coro)

        # Wait for all calls to complete
        results = await asyncio.gather(*coroutines, return_exceptions=True)

    # Explicit cleanup of coroutines and results
    coroutines.clear()
    del coroutines
    del results

    # Clear module history (test if this prevents memory leak)
    if hasattr(module, "history"):
        module.history.clear()

    # Explicitly delete the instance
    del module

    # Force garbage collection
    gc.collect()

    # Small delay to allow async cleanup
    await asyncio.sleep(0.01)


async def main():
    """Main test loop demonstrating memory leak."""

    # Get module type from environment variable
    module_type = os.environ.get("DSPY_MODULE", "chainofthought")
    module_name = "ChainOfThought" if module_type == "chainofthought" else "Predict"

    print("=" * 60)
    print("DSPy Memory Leak Reproduction")
    print("=" * 60)
    print(f"\nThis test demonstrates DSPy {module_name} memory usage")
    print("with module history clearing enabled.\n")

    # Configure DSPy with OpenAI (requires OPENAI_API_KEY env var)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY environment variable is required")
        print("Set your OpenAI API key and run again:")
        print("docker run --rm -e OPENAI_API_KEY='your-key-here' dspy-memory-leak")
        return

    print("✓ Using OpenAI LM with context manager")

    # Number of parallel calls per iteration
    NUM_PARALLEL_CALLS = 10

    # Get initial memory baseline
    initial_memory = get_memory()
    print(f"Initial memory: RSS={initial_memory['rss_mb']:.1f}MB")
    print(f"\nRunning test with {NUM_PARALLEL_CALLS} parallel calls per iteration...")
    print("Press Ctrl+C to stop")
    print("Memory growth will be logged to /app/memory_growth.log\n")

    # Initialize log file
    with open("/app/memory_growth.log", "w") as log_file:
        log_file.write("DSPy Memory Leak Test - Memory Growth Log\n")
        log_file.write("=" * 50 + "\n")
        log_file.flush()

    # Run test iterations indefinitely
    iteration = 0
    while True:
        iteration += 1

        # Run test iteration
        await test_iteration(NUM_PARALLEL_CALLS)

        # Check and log memory every iteration
        current_memory = get_memory()
        growth = current_memory["rss_mb"] - initial_memory["rss_mb"]

        # Create log message
        log_msg = f"Iteration {iteration:3d}: RSS={current_memory['rss_mb']:.1f}MB (growth={growth:+.1f}MB, rate={growth / iteration:.3f}MB/iter)"

        # Print to console with immediate flush
        print(log_msg, flush=True)

        # Also write to log file with immediate flush
        with open("/app/memory_growth.log", "a") as log_file:
            log_file.write(f"[{datetime.now().isoformat()}] {log_msg}\n")
            log_file.flush()

        # Small delay between iterations
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
