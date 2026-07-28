# 10. Transactions, Consistency & Consensus — Deep Dive

## Recap + Going Deeper Than `01-fundamentals/04-databases-fundamentals.md`

## Isolation Levels — With Concrete, Runnable-Style Examples
```sql
-- Setting isolation level explicitly (Postgres syntax)
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- ... queries ...
COMMIT;
```

### Dirty Read (only possible at Read Uncommitted — rarely used in practice)
```
Transaction A: UPDATE accounts SET balance = 500 WHERE id = 1;  -- NOT yet committed
Transaction B: SELECT balance FROM accounts WHERE id = 1;         -- reads 500 (uncommitted!)
Transaction A: ROLLBACK;                                          -- the 500 never actually happened
-- Transaction B made a decision based on data that was never real. Dangerous.
```

### Non-Repeatable Read (possible at Read Committed)
```
Transaction A: SELECT balance FROM accounts WHERE id = 1;  -- reads 1000
Transaction B: UPDATE accounts SET balance = 500 WHERE id = 1; COMMIT;
Transaction A: SELECT balance FROM accounts WHERE id = 1;  -- reads 500 -- DIFFERENT from before,
                                                            -- within the SAME transaction!
```

### Phantom Read (possible at Repeatable Read in some databases, prevented at Serializable)
```
Transaction A: SELECT COUNT(*) FROM orders WHERE status = 'pending';  -- returns 10
Transaction B: INSERT INTO orders (status) VALUES ('pending'); COMMIT;
Transaction A: SELECT COUNT(*) FROM orders WHERE status = 'pending';  -- returns 11 -- a
                                                                        -- "phantom" row appeared
```

## Distributed Transactions — Two-Phase Commit (2PC)
When a single logical transaction must span MULTIPLE separate databases (e.g., debit an account in Database A, credit an account in Database B), a normal single-database transaction can't help — you need a distributed transaction protocol.
```
Phase 1 (Prepare):
  Coordinator asks Database A: "can you commit this change?" -> A locks resources, says "yes, ready"
  Coordinator asks Database B: "can you commit this change?" -> B locks resources, says "yes, ready"

Phase 2 (Commit):
  If BOTH said yes: Coordinator tells both A and B to actually COMMIT
  If EITHER said no (or timed out): Coordinator tells both to ROLLBACK
```
**The real weakness of 2PC**: if the coordinator itself crashes between Phase 1 and Phase 2, participating databases can be left in an uncertain "prepared but not told what to do" state, holding locks indefinitely — this is exactly why 2PC is considered too fragile/slow for large-scale distributed systems, and why modern distributed databases (NewSQL, file 4) use consensus algorithms (Raft/Paxos) instead, which have better-defined failure/recovery behavior.

## Consensus Algorithms — Raft (the modern practical standard)
Recall from file 4: Raft lets a cluster of nodes agree on a sequence of operations even with node failures, via **leader election** and **majority-acknowledgment replication**.
```
Normal operation:
1. All nodes elect ONE leader (via a randomized-timeout voting mechanism, avoiding split votes)
2. ALL writes go through the leader
3. Leader replicates each write to followers, waits for a MAJORITY (not all) to acknowledge
4. Once majority acknowledges, the write is committed — durable even if a minority of
   nodes are down/unreachable

Leader failure:
1. Followers notice the leader stopped sending heartbeats
2. A new leader election happens automatically among remaining nodes
3. Cluster continues operating with zero manual intervention, as long as a majority
   of original nodes are still reachable
```
**Why "majority" specifically**: requiring only a majority (not all nodes) means the system tolerates up to floor((N-1)/2) node failures while continuing to operate correctly — e.g., a 5-node cluster tolerates 2 simultaneous node failures and keeps working, which is the actual mechanism behind the "self-healing," "no manual failover" marketing claims of CockroachDB/Spanner/etcd/Consul (all Raft or Paxos-based).

## Eventual Consistency — What It Actually Means in Practice
```
Write to Node A (accepted immediately, node A returns "success" to the client)
        |
   (asynchronous replication, might take milliseconds to seconds)
        v
Node B eventually receives the update too

If you read from Node B IMMEDIATELY after writing to Node A,
you might see the OLD value — this is "eventual" consistency:
it WILL become consistent eventually, just not necessarily instantly.
```
**Real business scenarios where this is genuinely fine**: a social media "like" count that's off by a few for a couple of seconds; a product view counter; a "last seen online" timestamp. **Real business scenarios where this is NOT fine**: an account balance, an inventory count that could lead to overselling the last unit of a product, anything involving money or safety.

## Consistency Models — The Full Spectrum (from weakest to strongest)
```
Eventual Consistency  ->  Read-Your-Writes  ->  Session Consistency  ->  Causal Consistency  ->  Strong Consistency
(weakest, fastest,          (you always see        (consistent within     (respects cause-       (strongest, matches
 most available)             your own writes,        your own session,     and-effect order        a single-machine
                              might not see            might not see          across related          database's
                              others' writes yet)      others' writes yet)   operations)              behavior exactly)
```
Cosmos DB (file 5) is notable for explicitly exposing this ENTIRE spectrum as a configuration choice per use case — most databases pick one point on this spectrum and that's just how they behave.

## Try It Yourself (conceptual)
1. Explain why 2PC's coordinator crash scenario is specifically dangerous, in your own words.
2. Why does Raft require a MAJORITY rather than ALL nodes to acknowledge a write? What would break if it required all nodes?
3. Pick 3 real features of an app you use daily and classify which consistency level each one probably needs (e.g., a bank balance vs a "likes" count vs a friend request notification).

## Interview Traps
- "What's the difference between 2PC and Raft/Paxos-based consensus?" — 2PC coordinates a single distributed transaction across heterogeneous systems but has fragile failure recovery (coordinator crash = stuck locks); Raft/Paxos are built for ongoing, repeated agreement within a single replicated system, with well-defined majority-based failure tolerance.
- "Why would eventual consistency ever be an acceptable choice?" — be ready with a real example (like counts, view counts) where brief staleness genuinely doesn't harm the business, versus one where it would be unacceptable (account balances) — this shows you can reason about tradeoffs rather than treating "strong consistency" as always strictly better.


---

<div align="center">

🙏 **राधे राधे | जय श्री हरिवंश** 🙏

*"Every act of genuine service, however small, ripples further than you can see."*

📘 Compiled with dedication by **[Ritik2703](https://github.com/Ritik2703)** — Data Engineering Handbook: Beginner to Production

</div>
