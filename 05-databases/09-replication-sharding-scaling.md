# 9. Replication, Sharding & Scaling — Every Real Pattern

## Vertical vs Horizontal Scaling
```
Vertical Scaling (Scale UP):   Add more CPU/RAM/faster disk to ONE existing server.
                                Simple, but has a hard ceiling (biggest available machine)
                                and a single point of failure.

Horizontal Scaling (Scale OUT): Add MORE servers, distributing load/data across them.
                                 Theoretically unlimited scale, but much more architecturally
                                 complex (this entire file is about managing that complexity).
```
**Real guidance**: always exhaust reasonable vertical scaling + query/index optimization first — it's dramatically simpler and often sufficient for surprisingly large workloads. Horizontal scaling patterns below are for when you've genuinely outgrown a single powerful machine.

## Replication — Copying Data for Availability & Read Scaling

### Primary-Replica (Master-Slave) Replication
```
                    [Primary/Master]
                 (accepts ALL writes)
                  /        |        \
        [Replica 1]  [Replica 2]  [Replica 3]
        (read-only)  (read-only)  (read-only)
```
Writes go to the primary, which asynchronously (or synchronously) streams changes to replicas. Application read queries can be routed to replicas, offloading read traffic from the primary — a very common, simple first scaling step for read-heavy workloads.
```python
# Common application pattern: route reads/writes to different connections
write_engine = create_engine("postgresql://primary-host/mydb")
read_engine = create_engine("postgresql://replica-host/mydb")

def get_order(order_id):
    return read_engine.execute("SELECT * FROM orders WHERE order_id = %s", order_id)

def create_order(order_data):
    return write_engine.execute("INSERT INTO orders ...", order_data)
```
**Replication lag** — the real production gotcha: replicas are usually a few milliseconds to a few seconds BEHIND the primary. A user who just placed an order and immediately refreshes their order history might not see it yet if that read hits a lagging replica — a very common real bug class, usually solved by routing "read your own write" scenarios to the primary specifically, or using a "read-after-write consistency" session pattern.

### Multi-Primary (Multi-Master) Replication
Multiple nodes can accept writes simultaneously — needed for true multi-region active-active systems (see cloud-native file 5). Requires conflict resolution logic (last-writer-wins, custom merge functions, or consensus-based ordering as in NewSQL/Spanner) since two regions could theoretically write conflicting changes to the same record within milliseconds of each other.

## Sharding — Splitting Data Across Multiple Database Servers

### Horizontal Sharding (Splitting Rows)
```
Shard 1: customers with customer_id % 4 == 0  (or hash-based, or range-based)
Shard 2: customers with customer_id % 4 == 1
Shard 3: customers with customer_id % 4 == 2
Shard 4: customers with customer_id % 4 == 3
```
Each shard is a separate, full database instance holding only a SUBSET of rows. The application (or a routing layer) must know which shard holds the data for a given key.

### Sharding Strategies — Real Tradeoffs
| Strategy | How it works | Tradeoff |
|---|---|---|
| **Range-based** | Shard by value ranges (e.g., A-M on shard 1, N-Z on shard 2) | Simple, but risks "hot shards" if data isn't evenly distributed (e.g., way more customers with names/IDs in one range) |
| **Hash-based** | Hash the shard key, distribute evenly by hash value | Even distribution, but range queries (e.g., "customers signed up in January") now must hit ALL shards |
| **Directory-based** | A lookup service maps each key to its shard explicitly | Most flexible (can rebalance individual keys), but the directory service itself becomes a critical dependency/potential bottleneck |

**Real production pain point — resharding**: as data grows unevenly, you eventually need to add more shards and REDISTRIBUTE existing data — this is one of the most operationally painful events in a sharded system's life, which is exactly why NewSQL databases (file 4) that handle this automatically are so valuable when you genuinely need this scale.

### Vertical Sharding / Functional Partitioning
Instead of splitting the SAME table's rows across servers, split DIFFERENT tables/services onto different database servers entirely — e.g., the `orders` database lives on one server, the `user_profiles` database lives on another. This is often the FIRST scaling step companies take (often alongside a broader move to microservices), well before needing to horizontally shard any single table.

## Read Scaling with Caching (often solves the problem before sharding is even needed)
```
Application --check cache first--> [Redis Cache] --cache miss--> [Primary Database]
                                          |
                                    (populate cache with result for next request)
```
**Cache invalidation strategies** (the famous "there are only two hard problems in computer science" joke applies directly here):
- **Write-through**: update the cache at the same time as the database write — cache always fresh, but adds write latency.
- **Write-behind**: write to cache immediately, asynchronously persist to the database later — fast, but risks data loss if the cache fails before persisting.
- **Cache-aside (lazy loading)**: application checks cache first; on a miss, reads from DB and populates the cache — the most common real-world pattern, simple and resilient, at the cost of the first request after any cache expiry being slower.

## Connection Pooling at Scale (a real, often-overlooked scaling bottleneck)
A database server has a hard limit on concurrent connections (Postgres default is often just 100). A microservices architecture with dozens of services, each opening their own connection pool, can easily exhaust this limit even on a powerful database server. **PgBouncer** (for Postgres) and similar connection poolers sit BETWEEN applications and the database, multiplexing many application-level connections onto a smaller number of actual database connections — an essential, often underappreciated piece of real production scaling architecture.

## Putting a Real Scaling Journey Together (how a company's architecture evolves)
```
Stage 1 (startup, <10K users):        Single Postgres instance, vertical scaling as needed.

Stage 2 (growing, 100K users):        Add a read replica for reporting/analytics queries;
                                       add Redis caching for hot read paths (product catalog).

Stage 3 (scaling, 1M+ users):         Functional/vertical sharding — split out high-traffic
                                       services (e.g., messaging, notifications) into their
                                       own dedicated databases; add PgBouncer connection pooling.

Stage 4 (hyper-scale, 10M+ users):    Horizontal sharding of the largest tables, OR migrate
                                       the highest-scale services to a NewSQL/NoSQL system
                                       purpose-built for this scale (Cassandra for write-heavy
                                       logs, DynamoDB for key-value access patterns, etc.)
```
This staged, problem-driven evolution (not jumping straight to the most complex solution) is exactly what real, successful engineering organizations do — and is the answer senior interviewers are hoping for over "just use microservices and shard everything from day one."

## Interview Traps
- "How would you scale a database handling 10x more traffic?" — always start with the STAGED approach above (vertical scaling/optimization -> caching -> read replicas -> functional splitting -> sharding), not jump straight to "shard it."
- "What's replication lag and how do you handle it?" — explain the "read your own write" problem and at least one mitigation (route specific reads to the primary, or session-consistency patterns).
- "Range-based vs hash-based sharding — which would you choose for a time-series logging table?" — hash-based avoids hot shards from naturally sequential timestamp-based writes all landing on the "newest" range shard; but acknowledge this makes time-range queries need to hit every shard, a real tradeoff to discuss.
