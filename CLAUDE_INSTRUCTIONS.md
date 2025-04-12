# Instructions for Claude

## Style Guide Reference

**IMPORTANT:** When working in this repository, always follow the style guidelines and best practices defined in the `CLAUDE.md` file. This file contains detailed information about:

- Single Responsibility Principle implementation
- Gang of Four design patterns and their applications
- Code organization guidelines
- Class design and naming conventions
- Interface design practices
- Code style standards
- Testing approaches

Before implementing new features or modifying existing code, review the `CLAUDE.md` file to ensure your changes align with the established patterns and principles.

## Object-Oriented Programming Best Practices

### Single Responsibility Principle (SRP)
- Each class should have only one reason to change
- A class should be responsible for only one part of the software's functionality
- Every class, module, or function should have a single, well-defined responsibility
- Apply SRP not only to classes but also to functions and modules
- Benefits: improved maintainability, easier testing, reduced dependencies

**Critical SRP Tests**: 
1. **The "And" Test**: Ask the question "What is the responsibility of this class?" If your answer contains the word "and", the class is doing too much and MUST be split into multiple classes.

2. **The Multi-Method Warning**: If a class has multiple public methods that seem to operate at different levels of abstraction or handle different concerns, it likely violates SRP.

3. **The Data Processing Chain Test**: If your class takes data, processes it in several distinct steps, and outputs a final result, each step should be its own class:
   - Input/parsing/conversion should be a separate class
   - Algorithm/calculation should be a separate class
   - Output/formatting should be a separate class

4. **The Mixed Concerns Check**: If your class mixes any of these concerns, split it immediately:
   - Business logic AND data access
   - Algorithm implementation AND configuration management
   - Data transformation AND validation
   - Core functionality AND error handling
   - Processing AND presentation

**SRP Implementation Guidelines**:
- Create small, focused classes with 1-3 primary methods
- Name classes after their single responsibility (e.g., `ImageFormatConverter`, not `ImageUtil`)
- Use composition to combine functionality from multiple single-responsibility classes
- If a class grows beyond 100 lines, review it for potential SRP violations
- When a class needs to do multiple things, create a façade/coordinator class that delegates to specialized classes

Remember: Violating SRP creates technical debt that compounds over time. Small classes with single responsibilities are easier to understand, test, reuse, and modify.

### Gang of Four (GoF) Design Patterns
The Gang of Four design patterns are 23 classic software design patterns introduced by Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides in their book "Design Patterns: Elements of Reusable Object-Oriented Software" (1994). These patterns are divided into three categories:

1. **Creational Patterns**: Handle object creation mechanisms
   - Factory Method, Abstract Factory, Singleton, Builder, Prototype

2. **Structural Patterns**: Deal with object composition
   - Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy

3. **Behavioral Patterns**: Focus on communication between objects
   - Chain of Responsibility, Command, Interpreter, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor

### Code Organization
- Each class should have its own file with a matching filename
- Abstract base classes (interfaces) should have their own file with a clear, descriptive name (e.g., `region_detector.py` for the `RegionDetector` interface)
- Don't use prefixes like "I" for interfaces; use meaningful base class names instead
- Never put multiple interfaces or classes in a single file
- Follow an intuitive folder structure organized by functionality
- Group related components in meaningful directories
- Separate abstract base classes from concrete implementations when appropriate
- Organize code by feature or domain rather than by technical type
- Use factory patterns for object creation
- Prefer composition over inheritance
- Maintain a clear, consistent naming convention that reflects the component's purpose

## Common Tasks

When working on the grayscale binary separator implementation:
1. Follow the variance-based detection approach outlined in research.md
2. Implement each component in its own file following SRP
3. Use appropriate design patterns as described in CLAUDE.md
4. Ensure all new code has proper unit tests

Remember to structure the implementation with interfaces and concrete implementations to allow for future flexibility.