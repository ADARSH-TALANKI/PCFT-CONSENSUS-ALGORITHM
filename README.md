PCFT: Privacy-Preserving Crash Fault-Tolerant Consensus:

Overview
This project implements a prototype of a Privacy-Preserving Crash Fault-Tolerant (PCFT) consensus algorithm for permissioned blockchain systems. The objective was to design and simulate a consensus mechanism that can tolerate node crashes while preserving transaction privacy using Schnorr Zero-Knowledge Proofs (ZKP).
The project focuses on understanding how consensus, fault tolerance, and cryptographic privacy can be combined in a practical distributed system.

Motivation:
Traditional crash fault-tolerant (CFT) consensus algorithms ensure availability and correctness but do not address transaction privacy. On the other hand, privacy-preserving techniques are often studied independently of consensus behavior.
The goal of this project was to explore how privacy guarantees can be integrated into a CFT consensus workflow, while keeping the system simple enough to reason about, simulate, and analyze.

System Architecture
The system follows a permissioned blockchain model and consists of the following components:
Certificate Authority (CA): Registers nodes and clients and issues credentials
Client: Creates transactions and generates zero-knowledge proofs
Primary Node: Coordinates consensus rounds
Replica Nodes: Validate transactions and participate in majority voting
Blockchain Layer: Stores committed blocks with Merkle root verification
API / UI Layer: Used to observe system behavior and consensus flow
Each node is assumed to be authenticated, and crash failures are considered instead of Byzantine faults.

Consensus Workflow
A client creates a transaction along with a Schnorr ZKP proving validity without revealing sensitive data
The transaction is sent to the primary node
The primary broadcasts the request to replica nodes
Replicas verify the proof and transaction correctness
A majority agreement leads to block commitment
In case of primary failure, a view-change mechanism is triggered
The system tolerates up to
𝑓=(𝑁−1)2
crash-faulty nodes, where 
N is the total number of replicas.

Privacy Mechanism (Schnorr ZKP):
Transaction privacy is ensured using the Schnorr Zero-Knowledge Proof protocol.
This allows a client to prove transaction authenticity and validity without revealing the underlying secret information.

The protocol includes:
Setup and key generation
Proof generation by the client
Proof verification by nodes during consensus
This ensures privacy while maintaining trust in transaction correctness.

Block Structure
Each block contains:
Block index
Timestamp
Transaction data
Merkle root for integrity verification
Hash of the previous block
This structure ensures immutability and tamper detection.

Implementation Highlights
Consensus and replica behavior simulated using Python
Schnorr ZKP implemented for transaction privacy
Majority-based agreement for block commitment
FastAPI used to visualize or interact with system behavior
Fault tolerance and view-change logic demonstrated conceptually

Project Context
This project was developed as part of a Distributed Systems / DSS coursework.
The implementation focuses on conceptual correctness, simulation, and understanding rather than production-level deployment.

Key Learnings
How crash fault tolerance differs from Byzantine fault tolerance
How privacy mechanisms like ZKP can be integrated into consensus
Trade-offs between performance, fault tolerance, and privacy
Importance of system architecture in distributed consensus design

Future Scope
Extending from CFT to Byzantine Fault Tolerance (BFT)
Integrating real networking instead of simulation
Performance benchmarking under node failures
Using real blockchain frameworks for deployment
