
### Concurrent sequence regression and generation for molecular language modeling**

The RT is a multitask Transformer that reformulates regression as a conditional sequence modeling task.
This yields a dichotomous language model that seamlessly integrates regression with property-driven conditional generation task.
**Further reading:** [arXiv preprint](https://arxiv.org/abs/2202.01338) and [GitHub development code](https://github.com/IBM/regression-transformer).

Each `algorithm_version` refers to one trained model. Each model can be used for **two tasks**, either to *predict* one (or multiple) properties of a molecule or to *generate* a molecule (given a seed molecule and a property constraint).