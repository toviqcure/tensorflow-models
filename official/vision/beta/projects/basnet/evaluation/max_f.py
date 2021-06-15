# Copyright 2020 The TensorFlow Authors. All Rights Reserved.
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
"""

This source code is a modified version of
https://github.com/xuebinqin/Binary-Segmentation-Evaluation-Tool

"""
# Import libraries
import numpy as np


class maxFscore(object):
  """Maximum F-score metric for basnet."""
  
  def __init__(self):
    """Constructs BASNet evaluation class."""
    self.reset_states()

  @property
  def name(self):
    return 'maxF'

  def reset_states(self):
    """Resets internal states for a fresh run."""
    self._predictions = []
    self._groundtruths = []

  def result(self):
    """Evaluates segmentation results, and reset_states."""
    metric_result = self.evaluate()
    # Cleans up the internal variables in order for a fresh eval next time.
    self.reset_states()
    return metric_result

  def evaluate(self):
    """Evaluates with masks from all images.

    Returns:
      f_max: maximum F-score value.
    """

    mybins = np.arange(0, 256)
    beta = 0.3
    precisions = np.zeros((len(self._groundtruths), len(mybins)-1))
    recalls = np.zeros((len(self._groundtruths), len(mybins)-1))

    for i, (true, pred) in enumerate(zip(self._groundtruths,
                                         self._predictions)):
      # Compute F-score
      true = self._mask_normalize(true)*255.0
      pred = self._mask_normalize(pred)*255.0
      pre, rec = self._compute_pre_rec(true, pred, mybins=np.arange(0,256))

      precisions[i,:] = pre
      recalls[i,:]    = rec

    precisions = np.sum(precisions,0)/(len(self._groundtruths)+1e-8)
    recalls    = np.sum(recalls,0)/(len(self._groundtruths)+1e-8)
    f          = (1+beta)*precisions*recalls/(beta*precisions+recalls+1e-8)
    f_max      = np.max(f)
    f_max = f_max.astype(np.float32)

    return f_max

  def _mask_normalize(self, mask):
    return mask/(np.amax(mask)+1e-8)

  def _compute_pre_rec(self, true, pred, mybins=np.arange(0,256)):
    # pixel number of ground truth foreground regions
    gt_num = true[true>128].size
    
    # mask predicted pixel values in the ground truth foreground region
    pp = pred[true>128]
    # mask predicted pixel values in the ground truth bacground region
    nn = pred[true<=128]

    pp_hist,pp_edges = np.histogram(pp,bins=mybins)
    nn_hist,nn_edges = np.histogram(nn,bins=mybins)

    pp_hist_flip = np.flipud(pp_hist)
    nn_hist_flip = np.flipud(nn_hist)

    pp_hist_flip_cum = np.cumsum(pp_hist_flip)
    nn_hist_flip_cum = np.cumsum(nn_hist_flip)

    precision = pp_hist_flip_cum/(pp_hist_flip_cum + nn_hist_flip_cum+1e-8) #TP/(TP+FP)
    recall = pp_hist_flip_cum/(gt_num+1e-8) #TP/(TP+FN)

    precision[np.isnan(precision)]= 0.0
    recall[np.isnan(recall)] = 0.0

    pre_len = len(precision)
    rec_len = len(recall)

    return np.reshape(precision,(pre_len)), np.reshape(recall,(rec_len))

  def _convert_to_numpy(self, groundtruths, predictions):
    """Converts tesnors to numpy arrays."""
    numpy_groundtruths = groundtruths.numpy()
    numpy_predictions = predictions.numpy()
    
    return numpy_groundtruths, numpy_predictions

  def update_state(self, groundtruths, predictions):
    """Update segmentation results and groundtruth data.

    Args:
      groundtruths : Tuple of single Tensor [batch, width, height, 1],
                     groundtruth masks. range [0, 1]
      predictions  : Tuple of signle Tensor [batch, width, height, 1],
                     predicted masks. range [0, 1]
    """
    groundtruths, predictions = self._convert_to_numpy(groundtruths[0],
                                                       predictions[0])
    for (true, pred) in zip(groundtruths, predictions):
      self._groundtruths.append(true)
      self._predictions.append(pred)
