import json
import logging
import os
from collections import defaultdict
from typing import Dict, List, Tuple

import mols2grid
import pandas as pd
from gt4sd.algorithms import (
    RegressionTransformerMolecules,
    RegressionTransformerProteins,
)
from gt4sd.algorithms.core import AlgorithmConfiguration
from rdkit import Chem
from terminator.selfies import decoder

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def get_application(application: str) -> AlgorithmConfiguration:
    """
    Convert application name to AlgorithmConfiguration.

    Args:
        application: Molecules or Proteins

    Returns:
        The corresponding AlgorithmConfiguration
    """
    if application == "Molecules":
        application = RegressionTransformerMolecules
    elif application == "Proteins":
        application = RegressionTransformerProteins
    else:
        raise ValueError(
            "Currently only models for molecules and proteins are supported"
        )
    return application


def get_inference_dict(
    application: AlgorithmConfiguration, algorithm_version: str
) -> Dict:
    """
    Get inference dictionary for a given application and algorithm version.

    Args:
        application: algorithm application (Molecules or Proteins)
        algorithm_version: algorithm version (e.g. qed)

    Returns:
        A dictionary with the inference parameters.
    """
    config = application(algorithm_version=algorithm_version)
    with open(os.path.join(config.ensure_artifacts(), "inference.json"), "r") as f:
        data = json.load(f)
    return data


def get_rt_name(x: Dict) -> str:
    """
    Get the UI display name of the regression transformer.

    Args:
        x: dictionary with the inference parameters

    Returns:
        The display name
    """
    return (
        x["algorithm_application"].split("Transformer")[-1]
        + ": "
        + x["algorithm_version"].capitalize()
    )


def draw_grid_predict(prediction: str, target: str, domain: str) -> str:
    """
    Uses mols2grid to draw a HTML grid for the prediction

    Args:
        prediction: Predicted sequence.
        target: Target molecule
        domain: Domain of the prediction (molecules or proteins)

    Returns:
        HTML to display
    """

    if domain not in ["Molecules", "Proteins"]:
        raise ValueError(f"Unsupported domain {domain}")

    seq = target.split("|")[-1]
    converter = (
        decoder
        if domain == "Molecules"
        else lambda x: Chem.MolToSmiles(Chem.MolFromFASTA(x))
    )
    try:
        seq = converter(seq)
    except Exception:
        logger.warning(f"Could not draw sequence {seq}")

    result = {"SMILES": [seq], "Name": ["Target"]}
    # Add properties
    for prop in prediction.split("<")[1:]:
        result[
            prop.split(">")[0]
        ] = f"{prop.split('>')[0].capitalize()} = {prop.split('>')[1]}"
    result_df = pd.DataFrame(result)
    obj = mols2grid.display(
        result_df,
        tooltip=list(result.keys()),
        height=900,
        n_cols=1,
        name="Results",
        size=(600, 700),
    )
    return obj.data


def draw_grid_generate(
    samples: List[Tuple[str]], domain: str, n_cols: int = 5, size=(140, 200)
) -> str:
    """
    Uses mols2grid to draw a HTML grid for the generated molecules

    Args:
        samples: The generated samples (with properties)
        domain: Domain of the prediction (molecules or proteins)
        n_cols: Number of columns in grid. Defaults to 5.
        size: Size of molecule in grid. Defaults to (140, 200).

    Returns:
        HTML to display
    """

    if domain not in ["Molecules", "Proteins"]:
        raise ValueError(f"Unsupported domain {domain}")

    if domain == "Proteins":
        try:
            smis = list(
                map(lambda x: Chem.MolToSmiles(Chem.MolFromFASTA(x[0])), samples)
            )
        except Exception:
            logger.warning(f"Could not convert some sequences {samples}")
    else:
        smis = [s[0] for s in samples]

    result = defaultdict(list)
    result.update({"SMILES": smis, "Name": [f"sample_{i}" for i in range(len(smis))]})

    # Create properties
    properties = [s.split("<")[1] for s in samples[0][1].split(">")[:-1]]
    # Fill properties
    for sample in samples:
        for prop in properties:
            value = float(sample[1].split(prop)[-1][1:].split("<")[0])
            result[prop].append(f"{prop} = {value}")

    result_df = pd.DataFrame(result)
    obj = mols2grid.display(
        result_df,
        tooltip=list(result.keys()),
        height=1100,
        n_cols=n_cols,
        name="Results",
        size=size,
    )
    return obj.data
