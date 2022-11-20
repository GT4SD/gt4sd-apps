import logging
import pathlib

import gradio as gr
import pandas as pd
from gt4sd.algorithms.conditional_generation.regression_transformer import (
    RegressionTransformer,
)
from gt4sd.algorithms.registry import ApplicationsRegistry
from utils import (
    draw_grid_generate,
    draw_grid_predict,
    get_application,
    get_inference_dict,
    get_rt_name,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def regression_transformer(
    algorithm: str,
    task: str,
    target: str,
    number_of_samples: int,
    search: str,
    temperature: float,
    tolerance: int,
    wrapper: bool,
    fraction_to_mask: float,
    property_goal: str,
    tokens_to_mask: str,
    substructures_to_mask: str,
    substructures_to_keep: str,
):

    if task == "Predict" and wrapper:
        logger.warning(
            f"For prediction, no sampling_wrapper will be used, ignoring: fraction_to_mask: {fraction_to_mask}, "
            f"tokens_to_mask: {tokens_to_mask}, substructures_to_mask={substructures_to_mask}, "
            f"substructures_to_keep: {substructures_to_keep}."
        )
        sampling_wrapper = {}
    elif not wrapper:
        sampling_wrapper = {}
    else:
        substructures_to_mask = (
            []
            if substructures_to_mask == ""
            else substructures_to_mask.replace(" ", "").split(",")
        )
        substructures_to_keep = (
            []
            if substructures_to_keep == ""
            else substructures_to_keep.replace(" ", "").split(",")
        )
        tokens_to_mask = [] if tokens_to_mask == "" else tokens_to_mask.split(",")

        property_goals = {}
        if property_goal == "":
            raise ValueError(
                "For conditional generation you have to specify `property_goal`."
            )
        for line in property_goal.split(","):
            property_goals[line.split(":")[0].strip()] = float(line.split(":")[1])

        sampling_wrapper = {
            "substructures_to_keep": substructures_to_keep,
            "substructures_to_mask": substructures_to_mask,
            "text_filtering": False,
            "fraction_to_mask": fraction_to_mask,
            "property_goal": property_goals,
        }
    algorithm_application = get_application(algorithm.split(":")[0])
    algorithm_version = algorithm.split(" ")[-1].lower()
    config = algorithm_application(
        algorithm_version=algorithm_version,
        search=search.lower(),
        temperature=temperature,
        tolerance=tolerance,
        sampling_wrapper=sampling_wrapper,
    )
    model = RegressionTransformer(configuration=config, target=target)
    samples = list(model.sample(number_of_samples))

    if task == "Predict":
        return draw_grid_predict(samples[0], target, domain=algorithm.split(":")[0])
    else:
        return draw_grid_generate(samples, domain=algorithm.split(":")[0])


if __name__ == "__main__":

    # Preparation (retrieve all available algorithms)
    all_algos = ApplicationsRegistry.list_available()
    rt_algos = list(
        filter(lambda x: "RegressionTransformer" in x["algorithm_name"], all_algos)
    )
    rt_names = list(map(get_rt_name, rt_algos))

    properties = {}
    for algo in rt_algos:
        application = get_application(
            algo["algorithm_application"].split("Transformer")[-1]
        )
        data = get_inference_dict(
            application=application, algorithm_version=algo["algorithm_version"]
        )
        properties[get_rt_name(algo)] = data
    properties

    # Load metadata
    metadata_root = (
        pathlib.Path(__file__)
        .parent.resolve()
        .parent.parent.parent.parent.joinpath("model_cards")
    )

    examples = pd.read_csv(
        metadata_root.joinpath("regression_transformer_examples.csv"), header=None
    ).fillna("")

    with open(metadata_root.joinpath("regression_transformer_article.md"), "r") as f:
        article = f.read()
    with open(
        metadata_root.joinpath("regression_transformer_description.md"), "r"
    ) as f:
        description = f.read()

    demo = gr.Interface(
        fn=regression_transformer,
        title="Regression Transformer",
        inputs=[
            gr.Dropdown(rt_names, label="Algorithm version", value="Molecules: Qed"),
            gr.Radio(choices=["Predict", "Generate"], label="Task", value="Generate"),
            gr.Textbox(
                label="Input", placeholder="CC(C#C)N(C)C(=O)NC1=CC=C(Cl)C=C1", lines=1
            ),
            gr.Slider(
                minimum=1, maximum=50, value=10, label="Number of samples", step=1
            ),
            gr.Radio(choices=["Sample", "Greedy"], label="Search", value="Sample"),
            gr.Slider(minimum=0.5, maximum=2, value=1, label="Decoding temperature"),
            gr.Slider(minimum=5, maximum=100, value=30, label="Tolerance", step=1),
            gr.Radio(choices=[True, False], label="Sampling Wrapper", value=True),
            gr.Slider(minimum=0, maximum=1, value=0.5, label="Fraction to mask"),
            gr.Textbox(label="Property goal", placeholder="<qed>:0.75", lines=1),
            gr.Textbox(label="Tokens to mask", placeholder="N, C", lines=1),
            gr.Textbox(
                label="Substructures to mask", placeholder="C(=O), C#C", lines=1
            ),
            gr.Textbox(
                label="Substructures to keep", placeholder="C1=CC=C(Cl)C=C1", lines=1
            ),
        ],
        outputs=gr.HTML(label="Output"),
        article=article,
        description=description,
        examples=examples.values.tolist(),
    )
    demo.launch(debug=True, show_error=True)
