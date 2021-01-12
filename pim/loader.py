# Copyright 2020 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Loader for pre-trained PIM models."""

import io
import json
import os
import urllib
import zipfile
from perceptual_quality.pim import config
from perceptual_quality.pim import models

# Default URL to fetch model weights from.
URL_PREFIX = "https://storage.googleapis.com/tensorflow_compression/pim"


def download_model(model_name, weights_cache):
  """Downloads and caches model weights from web storage."""
  url = f"{URL_PREFIX}/{model_name}.zip"
  with urllib.request.urlopen(url) as request:
    buffer = io.BytesIO(request.read())
  with zipfile.ZipFile(buffer) as archive:
    os.makedirs(weights_cache, exist_ok=True)
    archive.extractall(weights_cache)


def load_trained(model_name, weights_cache="/tmp/pim_weights"):
  """Loads and instantiates a trained PIM model.

  Instantiates models from the paper:

  > "An Unsupervised Information-Theoretic Perceptual Quality Metric"<br />
  > S. Bhardwaj, I. Fischer, J. Ballé, T. Chinen<br />
  > https://arxiv.org/abs/2006.06752

  Note that the code and trained models provided here are reimplementations of
  the models used in the paper. There may thus be minor performance
  discrepancies (we found them to have slightly worse performance on BAPPS-2AFC
  but better performance on BAPPS-JND).

  Args:
    model_name: String. Either "pim-1" or "pim-5" for 1 or 5 mixture components,
      respectively. For 1 component, the symmetrized KL divergence can be more
      easily evaluated because it collapses to the squared Euclidean distance.
    weights_cache: String. File path for caching model weights downloaded from
      web storage.

  Returns:
    Appropriately configured `PIM` instance ready to be used.
  """
  if URL_PREFIX == "test":
    # Do not load trained weights in a unit test scenario.
    params = config.get_params()
    return models.PIM(params)
  path = os.path.join(weights_cache, model_name)
  if not os.path.exists(path):
    download_model(model_name, weights_cache)
  with open(os.path.join(path, "config.json"), "rb") as f:
    params = json.load(f)
  pim = models.PIM(params)
  pim.load_weights(os.path.join(path, "weights"))
  return pim
