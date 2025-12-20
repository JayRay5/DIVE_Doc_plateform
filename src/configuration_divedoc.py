import sys
from pathlib import Path
parent_root = Path().resolve().parent.parent 
sys.path.append(str(parent_root))

from transformers import PretrainedConfig, DonutSwinConfig, GemmaConfig, CONFIG_MAPPING
from typing import Tuple, Literal



class PamConfig(PretrainedConfig): 
     model_type = "pam"
     def __init__(
        self,
        sequence_mapping_layer_type: Literal["linear_projection","bilinear_interpolation"] = "bilinear_interpolation",
        student_fmap_dim: Tuple[int,int]=(80,60),
        student_embedding_dim: int = 1024,
        teacher_fmap_dim: Tuple[int,int] = (64,64),
        teacher_embedding_dim: int = 1152,
        **kwargs,
    ):
        self.sequence_mapping_layer_type = sequence_mapping_layer_type
        self.student_fmap_dim = student_fmap_dim
        self.student_embedding_dim = student_embedding_dim
        self.teacher_fmap_dim = teacher_fmap_dim
        self.teacher_embedding_dim = teacher_embedding_dim
        super().__init__(**kwargs)


class SwinPamVisionEncoderConfig(PretrainedConfig): 
    model_type = "swinpam"
    sub_configs = {"encoder_config": DonutSwinConfig, "pam_config": PamConfig}
    def __init__(
        self,
        encoder_config: DonutSwinConfig = None,
        pam_config: PamConfig = None,
        **kwargs
    ):
        self.encoder_config = encoder_config
        self.pam_config = pam_config

        if isinstance(self.encoder_config, dict):
            encoder_config["model_type"] = (
                encoder_config["model_type"] if "model_type" in encoder_config else "donut-swin"
            )
            if encoder_config["model_type"] == "donut-swin":
                self.encoder_config = DonutSwinConfig(**encoder_config)
            else:
                print(f"Encoder type: {encoder_config['model_type']}")
                self.encoder_config = CONFIG_MAPPING[encoder_config["model_type"]](**encoder_config)
        
        '''
        elif encoder_config is None:
            print("coucou2")
            self.encoder_config = DonutSwinConfig()
        '''

        if isinstance(self.pam_config, dict):
            '''
            pam_config["model_type"] = (
                pam_config["model_type"] if "model_type" in pam_config else "pam"
            )
            '''
            if pam_config["model_type"] == "pam":
                self.pam_config = PamConfig(**pam_config)
            else:
                raise ValueError(f"pam_config['model_type'] should be 'pam', got {pam_config['model_type']}")
        '''
        elif pam_config is None:
            self.pam_config = PamConfig()
        '''
        super().__init__(**kwargs)


class DIVEdocConfig(PretrainedConfig):
    keys_to_ignore_at_inference = ["past_key_values"]
    sub_configs = {"vision_config": SwinPamVisionEncoderConfig, "text_config": GemmaConfig}
    model_type = "DIVEdoc"
    def __init__(
        self,
        vision_config=None,
        text_config=None,
        ignore_index=-100,
        image_token_index=256000,
        vocab_size=257152,
        projection_dim=2048,
        hidden_size=2048,
        #_attn_implementation_autoset = True,
        **kwargs,
    ):
        self._ignore_index = ignore_index
        self.image_token_index = image_token_index
        self._vocab_size = vocab_size
        self.projection_dim = projection_dim
        self.hidden_size = hidden_size
        self.vision_config = vision_config
        self.is_encoder_decoder = False
        #self._attn_implementation_autoset = _attn_implementation_autoset
    

        if isinstance(self.vision_config, dict):
            vision_config["model_type"] = (
                vision_config["model_type"] if "model_type" in vision_config else "swinpam"
            )
            if vision_config["model_type"] == "swinpam":
                self.vision_config = SwinPamVisionEncoderConfig(encoder_config=vision_config["encoder_config"],pam_config=vision_config["pam_config"])
            else:
                self.vision_config = CONFIG_MAPPING[vision_config["model_type"]](**vision_config)
        elif vision_config is None:
            self.vision_config = get_vision_config("swinpam")

        self.text_config = text_config
        if isinstance(self.text_config, dict):
            text_config["model_type"] = text_config["model_type"] if "model_type" in text_config else "gemma"
            self.text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        elif text_config is None:
            self.text_config = CONFIG_MAPPING["gemma"](
                hidden_size=2048,
                num_hidden_layers=18,
                intermediate_size=16384,
                num_attention_heads=8,
                num_key_value_heads=1,
                is_encoder_decoder=False,
                vocab_size=vocab_size,
            )
    
        self.text_config.num_image_tokens = self.vision_config.pam_config.teacher_fmap_dim[0] *\
                                            self.vision_config.pam_config.teacher_fmap_dim[1]
        self.vision_config.projection_dim = projection_dim
        super().__init__(**kwargs)

    def to_dict(self):
        output = super().to_dict()
        output.pop("_ignore_index", None)
        return output