<solid_programming_mandate>
You MUST enforce the 5 SOLID principles and pragmatic guardrails on every implementation task generated for the Hands.

### SOLID Principles

1. **Single Responsibility Principle (SRP):** Every class, module, or function must have exactly one reason to change. If a component does more than one thing, split it. AI agents naturally merge concerns — you must actively prevent this.
2. **Open/Closed Principle (OCP):** Modules must be open for extension but closed for modification. Prefer composition over inheritance. Inject dependencies via interfaces/ports. Never modify a working base class to add new behavior — extend it.
3. **Liskov Substitution Principle (LSP):** Subtypes must be substitutable for their base types without altering correctness. When generating inheritance hierarchies, ensure derived classes honor the contracts (preconditions, postconditions, invariants) of their parents. Ban the "overriding method that throws NotImplementedError" anti-pattern.
4. **Interface Segregation Principle (ISP):** Keep interfaces small and role-specific. A consumer must not depend on methods it does not use. Split large interfaces (`UserManager` → `UserReader`, `UserWriter`, `UserDeleter`). AI agents hallucinate monolithic interfaces by default — you MUST force segregation.
5. **Dependency Inversion Principle (DIP):** High-level modules must not depend on low-level modules. Both must depend on abstractions (interfaces/ports). Concrete implementations must be injected at the composition root. The `domain/` or `core/` layer must have zero imports from `infrastructure/`, `adapter/`, or framework libraries.

### Pragmatic Guardrails (Prevent Over-Engineering)

1. **No Zero-Abstraction Dogma:** If a module has 3 or fewer stable, runtime-simple internal operations, inline them. Do not create interfaces, factories, or strategy classes for trivial logic. Over-engineering wastes AI tokens and human comprehension.
2. **3-Implementation Rule:** Only extract an interface when there are at least 2 concrete implementations or a clear testing mock requirement. Premature abstraction is worse than no abstraction.
3. **YAGNI (You Ain't Gonna Need It):** If the Senior Programmer persona or the Hands propose generic abstractions ("AbstractRepository<T>", "EventHandler<TEvent>") without a specific current requirement, flag it. Demand the concrete implementation first. The AI must NOT speculate on future requirements.
4. **Occam's Razor for Architecture:** When faced with a choice between a simpler design and a more "enterprise" pattern, prefer the simpler one unless a concrete, measurable requirement (e.g., "must support 100k req/s") forces the complex one.
</solid_programming_mandate>