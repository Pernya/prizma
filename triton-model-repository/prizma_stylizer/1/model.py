import numpy as np
import triton_python_backend_utils as pb_utils


class TritonPythonModel:
    def initialize(self, args):
        self.model_config = args["model_config"]

    def execute(self, requests):
        responses = []

        for request in requests:
            image = pb_utils.get_input_tensor_by_name(request, "IMAGE_B64").as_numpy()
            output = pb_utils.Tensor("IMAGE_B64", np.array([image[0]], dtype=object))
            responses.append(pb_utils.InferenceResponse(output_tensors=[output]))

        return responses
