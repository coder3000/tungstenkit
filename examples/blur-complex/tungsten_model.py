import time
from typing import Dict, List, Tuple

from PIL import ImageFilter

from tungstenkit import BaseIO, Field, Image, Option, define_model


class Input(BaseIO):
    image: Image = Field(description="Image to blur")
    gaussian_kernel_radius: int = Option(
        5, description="Gaussian kernel size for blurring", ge=1, le=10
    )
    delay: float = Option(1.0, description="Delay in seconds", ge=0.1, le=60.0)


class Output(BaseIO):
    blurred: Image


@define_model(
    input=Input,
    output=Output,
    demo_output=Output,
    readme_md="README.md",
    gpu=False,
    python_packages=["pillow"],
)
class ModelData:
    def setup(self):
        print("setup")
        pass

    def predict(self, inputs: List[Input]) -> List[Output]:
        images = [inp.image.to_pil_image() for inp in inputs]
        converted = []
        for img in images:
            converted.append(img.filter(ImageFilter.GaussianBlur(radius=5)).convert("RGB"))
        return [Output(blurred=Image.from_pil_image(img)) for img in images]

    def predict_demo(self, inputs: List[Input]) -> Tuple[List[Output], List[Dict]]:
        opt = inputs[0]
        pil_images = [inp.image.to_pil_image() for inp in inputs]
        for i, pil_img in enumerate(pil_images):
            print(
                f"[{i+1:02} / {len(pil_images):02}]"
                + f"running image processing (delay: {opt.delay})",
                end="",
            )
            pil_img.filter(ImageFilter.GaussianBlur(radius=opt.gaussian_kernel_radius)).convert(
                "RGB"
            ).save(f"image-{i}.jpg")
            time.sleep(opt.delay)
            print(" done")

        blurred_images = [Image.from_path(path=f"image-{i}.jpg") for i in range(len(pil_images))]
        demo_outputs = [
            {"original": img, "blurred": blurred} for img, blurred in zip(inputs, blurred_images)
        ]
        return [Output(blurred=blurred) for blurred in blurred_images], demo_outputs