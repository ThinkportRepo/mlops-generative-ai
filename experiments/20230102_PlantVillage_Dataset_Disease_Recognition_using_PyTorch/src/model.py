from torch.hub import load_state_dict_from_url
from torchvision import models
from torchvision.models import WeightsEnum


def get_state_dict(self, *args, **kwargs):
    kwargs.pop("check_hash")
    return load_state_dict_from_url(self.url, *args, **kwargs)


def model_config(model_name='mobilenetv3_large'):
    # https://github.com/pytorch/vision/issues/7744#issuecomment-1757321451
    WeightsEnum.get_state_dict = get_state_dict
    model = {
        'mobilenetv3_large': models.mobilenet_v3_large(weights='DEFAULT'),
        'shufflenetv2_x1_5': models.shufflenet_v2_x1_5(weights='DEFAULT'),
        'efficientnetb0': models.efficientnet_b0(weights='DEFAULT')
    }
    return model[model_name]


def build_model(model_name='mobilenetv3_large', fine_tune=True, num_classes=10):
    model = model_config(model_name)
    if fine_tune:
        print('[INFO]: Fine-tuning all layers...')
        for params in model.parameters():
            params.requires_grad = True
    elif not fine_tune:
        print('[INFO]: Freezing hidden layers...')
        for params in model.parameters():
            params.requires_grad = False
    if model_name == 'mobilenetv3_large':
        model.classifier[3].out_features = num_classes
    if model_name == 'shufflenetv2_x1_5':
        model.fc.out_features = num_classes
    if model_name == 'mobilenetv3_large':
        model.classifier[1].out_features = num_classes
    return model
