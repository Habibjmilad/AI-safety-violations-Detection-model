from tflite_runtime.interpreter import Interpreter
from PIL import Image
import numpy as np

# Load TFLite model
model_path = 'path\\to\\your\\model.tflite'
interpreter = Interpreter(model_path)
interpreter.allocate_tensors()

# Get input and output tensors
input_tensor_index = interpreter.get_input_details()[0]['index']
output = interpreter.tensor(interpreter.get_output_details()[0]['index'])

# Load an input image (modify this according to your application)
input_image_path = 'path\\to\\your\\input_image.jpg'
input_image = Image.open(input_image_path)
input_tensor = np.array(input_image).astype(np.uint8)
input_tensor = np.expand_dims(input_tensor, axis=0)

# Set input tensor
interpreter.set_tensor(input_tensor_index, input_tensor)

# Run inference
interpreter.invoke()

# Get the output tensor
output_tensor = output()

# Process the output as needed for your application
print(output_tensor)
