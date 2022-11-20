# Model card -- Regression Transformer 

## Parameters

### Algorithm Version:
Which model checkpoint to use (trained on different datasets).

### Task
Whether the multitask model should be used for property prediction or conditional generation (default).

### Input
The input sequence. In the default setting (where `Task` is *Generate* and `Sampling Wrapper` is *True*) this can be a seed SMILES (for the molecule models) or amino-acid sequence (for the protein models). The model will locally adapt the seed sequence by masking `Fraction to mask` of the tokens.
If the `Task` is *Predict*, the sequences are given as SELFIES for the molecule models. Moreover, the tokens that should be predicted (`[MASK]` in the input) have to be given explicitly. Populate the examples to understand better. 
NOTE: When setting `Task` to *Generate*, and `Sampling Wrapper` to *False*, the user has maximal control about the generative process and can explicitly decide which tokens should be masked.

### Number of samples
How many samples should be generated (between 1 and 50). If `Task` is *Predict*, this has to be set to 1.

### Search
Decoding search method. Use *Sample* if `Task` is *Generate*. If `Task` is *Predict*, use *Greedy*.

### Tolerance
Precision tolerance; only used if `Task` is *Generate*. This is a single float between 0 and 100 for the the tolerated deviation between desired/primed property and predicted property of the generated molecule. Given in percentage with respect to the property range encountered during training.
NOTE: The tolerance is *only* used for post-hoc filtering of the generated samples.

### Sampling Wrapper
Only used if `Task` is *Generate*. If set to *False*, the user has to provide a full RT-sequence as `Input` and has to **explicitly** decide which tokens are masked (see example below). This gives full control but is tedious. Instead, if `Sampling Wrapper` is set to *True*, the RT stochastically determines which parts of the sequence are masked.
**NOTE**: All below arguments only apply if `Sampling Wrapper` is *True*.

#### Fraction to mask
Specifies the ratio of tokens that can be changed by the model. Argument only applies if `Task` is *Generate* and `Sampling Wrapper` is *True*.

#### Property goal
Specifies the desired target properties for the generation. Need to be given in the format `<prop>:value`. If the model supports multiple properties, give them separated by a comma `,`. Argument only applies if `Task` is *Generate* and `Sampling Wrapper` is *True*.

#### Tokens to mask
Optionally specifies which tokens (atoms, bonds etc) can be masked. Please separate multiple tokens by comma (`,`). If not specified, all tokens can be masked. Argument only applies if `Task` is *Generate* and `Sampling Wrapper` is *True*.

#### Substructures to mask
Optionally specifies a list of substructures that should *definitely* be masked (excluded from stochastic masking). Given in SMILES format. If multiple are provided, separate by comma (`,`). Argument only applies if `Task` is *Generate* and `Sampling Wrapper` is *True*.
*NOTE*: Most models operate on SELFIES and the matching of the substructures occurs in SELFIES simply on a string level.

#### Substructures to keep
Optionally specifies a list of substructures that should definitely be present in the target sample (i.e., excluded from stochastic masking). Given in SMILES format. Argument only applies if `Task` is *Generate* and `Sampling Wrapper` is *True*.
*NOTE*: This keeps tokens even if they are included in `tokens_to_mask`.
*NOTE*: Most models operate on SELFIES and the matching of the substructures occurs in SELFIES simply on a string level.

## Citation

```bib
@article{born2022regression,
  title={Regression Transformer: Concurrent Conditional Generation and Regression by Blending Numerical and Textual Tokens},
  author={Born, Jannis and Manica, Matteo},
  journal={arXiv preprint arXiv:2202.01338},
  note={Spotlight talk at ICLR workshop on Machine Learning for Drug Discovery},
  year={2022}
}
```

