# Event Loop Experiment

## Experiment 1: Non-blocking Sequential Awaiting

### Actual Output

- A starts
- A ends
- B starts
- B ends
- Total elapsed time: 3.00 seconds

### Observations

Both coroutines use `await asyncio.sleep()` for non-blocking delays. However, because the coroutines are awaited sequentially inside `main()`, Task A finishes before Task B begins.

The total elapsed time was 3.00 seconds, which matches the combined waiting periods of two seconds and one second.

Although `asyncio.sleep()` allows the event loop to perform other work during a pause, no other coroutine was scheduled to execute during these waiting periods. This demonstrates that using `async` and `await` alone does not automatically create concurrent execution.

## Experiment 2: Non-blocking Concurrent Execution

### Predicted and Actual Output

- A starts
- B starts
- B ends
- A ends
- Total elapsed time: 2.00 seconds

### Observations

The actual execution order and elapsed time matched my prediction.

Using `asyncio.create_task()` allowed both coroutines to be scheduled concurrently without using `asyncio.gather()`. When Task A reached its non-blocking sleep, it yielded control to the event loop, allowing Task B to begin executing.

Task B finished before Task A because it had a shorter waiting period.

The total elapsed time decreased from 3.00 seconds to 2.00 seconds, representing approximately a 33.3% reduction in execution time.

### Fairness Note

Both experiments used the same coroutines, delay lengths, runtime environment, and timing approach. Only the execution strategy changed.

## Experiment 3: Blocking the Event Loop

### Execution Strategy

I replaced `await asyncio.sleep(2)` in Task A with `time.sleep(2)` while keeping Task B and the concurrent scheduling strategy unchanged.

### Predicted Output

- A starts
- A ends
- B starts
- B ends
- Expected elapsed time: approximately 3 seconds

### Actual Output

- A starts
- A ends
- B starts
- B ends
- Total elapsed time: 3.01 seconds

### Observations

The actual execution order and elapsed time matched my prediction. Although both coroutines were scheduled concurrently using `asyncio.create_task()`, Task B could not begin while Task A was executing `time.sleep(2)`.

The blocking sleep prevented the event loop from progressing until Task A finished. As a result, the waiting periods accumulated instead of overlapping.

The total elapsed time increased from 2.00 seconds to 3.01 seconds, representing a 50.5% increase in execution time.

### Fairness Note

Both concurrent experiments used the same delay lengths, scheduling strategy, runtime environment, and timing method. The only change was replacing Task A's non-blocking sleep with a blocking sleep.

### Stall Rule

Blocking synchronous operations inside a coroutine prevent other coroutines on the same event loop from progressing, even when those coroutines have been scheduled concurrently. Non-blocking awaitable operations allow the event loop to continue executing other scheduled work.

## Event Loop Stall Rule

A single blocking call inside the event-loop thread prevents all other coroutines on that event loop from making progress until the blocking operation finishes, even when they are scheduled concurrently.

## Experiment 4: Repaired Non-Blocking Execution

### Change Made

Replaced `time.sleep(2)` with `await asyncio.sleep(2)` in Task A while keeping both coroutines scheduled concurrently and leaving Task B unchanged.

### Actual Output

    A starts
    B starts
    B ends
    A ends
    Total elapsed time: 2.00 seconds

### Observations

Replacing the blocking wait with a non-blocking wait restored event-loop interleaving. Both coroutines were able to overlap their waiting periods, reducing the total execution time from 3.01 seconds to 2.00 seconds.

## Event Loop Stall Rule

A single blocking call inside the event-loop thread prevents other coroutines on that event loop from making progress until the blocking operation finishes, even when they are scheduled concurrently.

## Final Experiment Comparison

| Experiment | Elapsed Time |
|---|---|
| Sequential awaiting | 3.00 seconds |
| Non-blocking concurrent execution | 2.00 seconds |
| Blocking concurrent execution | 3.01 seconds |
| Repaired concurrent execution | 2.00 seconds |