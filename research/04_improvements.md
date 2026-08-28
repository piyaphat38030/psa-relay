# Plan improvement pass (applied)

1. Switched from pydantic/FastAPI to stdlib HTTP — runs on Python 3.14 with zero deps.
2. Fixed recovery simulator bug (scored “before” after mutation) so restow savings are real.
3. Tuned scenarios so late feeder is recoverable (not hopeless +14h miss).
4. Cutoff extension now mutates twin state on approve — demo shows residual risk fall to zero.
5. Critic still rejects PLAN-X on crane outage (infeasible capacity).
6. Uncertainty scenario keeps residual risk on purpose — shows honesty under incomplete data.
7. Deliverables: 10-slide McKinsey deck, speaker script, architecture PDF, video shot list.
