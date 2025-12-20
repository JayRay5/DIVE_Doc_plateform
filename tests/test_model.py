import torch
import pytest
from PIL import Image
from pathlib import Path


@pytest.mark.slow
class TestDiveDocModel:
    """Test DiveDoc model."""

    def test_forward_pass_generation(self, processor, model):
        base_path = Path(__file__).parent 
        image_path = base_path / "data" / "img_test.jpg"
        image = Image.open(image_path).convert("RGB")
        question = "What is the title of this document?"

        inputs = processor(
            text=question, 
            images=image, 
            return_tensors="pt",
            padding=True
        ).to(model.device)
        input_length = inputs["input_ids"].shape[-1]


        with torch.inference_mode():
            output_ids = model.generate( **inputs, max_new_tokens=100)

        # Type check
        assert isinstance(output_ids, torch.Tensor)
        
        # Dim check
        assert output_ids.shape[0] == 1 #batch size

        generated_ids = output_ids[0][input_length:]
        assert generated_ids.shape[0] > 0 #generated sequence length

        answer = processor.decode(generated_ids, skip_special_tokens=True)
        assert len(answer.strip()) > 0 #answer length