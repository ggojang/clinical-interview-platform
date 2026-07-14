# Mission

Build an open, traceable, AI-native Clinical Interview Knowledge Factory that continuously generates, validates, compiles, evaluates, and evolves reusable interview knowledge for Primary Care.

Knowledge is the product. Runtime is one executor.

The framework must help an AI conduct structured clinical interviews without hiding state, evidence, uncertainty, or safety decisions inside an opaque prompt.

The framework must:

1. listen to a patient's open narrative;
2. extract only supported clinical facts;
3. maintain a longitudinal Clinical Memory;
4. detect missing, conflicting, and safety-critical information;
5. select one useful next question;
6. preserve provenance for every assertion;
7. evaluate itself against reproducible simulations.

The project succeeds when interview knowledge and behavior can be inspected, tested, criticized, compiled, and improved independently of any single model provider or Runtime implementation.

## Version 0.1 mission

Demonstrate the complete loop for cough:

`utterance → facts → memory → active pattern → gaps → safety → next question → evaluation`

Diagnosis, treatment recommendation, and production deployment are outside Version 0.1.
