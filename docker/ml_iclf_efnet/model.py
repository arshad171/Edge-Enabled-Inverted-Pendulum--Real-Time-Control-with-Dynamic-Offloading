import torch as th
import torchvision.models as tv_models

batch_size = 2

def get_data(batch_size):
    return th.randn(batch_size, 3, 224, 224)

class Model:
    def __init__(self):
        # weights = th.load("module/weights.pth")
        self.model = tv_models.efficientnet_v2_l(weights=None)

    def predict(self, batch_size=batch_size):
        data = get_data(batch_size)
        preds = self.model(data)

        return preds.detach().numpy().tolist()



