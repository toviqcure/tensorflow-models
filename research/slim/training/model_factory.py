# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Contains a factory for building various models."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import google3
import tensorflow as tf

from nets import alexnet
from nets import cifarnet
from nets import inception
from nets import lenet
from nets import overfeat
from nets import resnet_utils
from nets import resnet_v1
from nets import resnet_v2
from nets import vgg

slim = tf.contrib.slim


def get_model(name, num_classes, weight_decay=0.0, is_training=False):
  """Returns a model_fn such as `logits, end_points = model_fn(images)`.

  Args:
    name: The name of the model.
    num_classes: The number of classes to use for classification.
    weight_decay: The l2 coefficient for the model weights.
    is_training: `True` if the model is being used for training and `False`
      otherwise.

  Returns:
    model_fn: A function that applies the model to a batch of images. It has
      the following signature:
        logits, end_points = model_fn(images)
  Raises:
    ValueError: If model `name` is not recognized.
  """
  if name == 'cifarnet':
    default_image_size = cifarnet.cifarnet.default_image_size
    def func(images):
      with slim.arg_scope(cifarnet.cifarnet_arg_scope(
          weight_decay=weight_decay)):
        return cifarnet.cifarnet(images, num_classes,
                                 is_training=is_training)
    model_fn = func
  elif name == 'inception_v1':
    default_image_size = inception.inception_v1.default_image_size
    def func(images):
      with slim.arg_scope(inception.inception_v1_arg_scope(
          weight_decay=weight_decay)):
        return inception.inception_v1(images,
                                      num_classes,
                                      is_training=is_training)
    model_fn = func
  elif name == 'inception_v2':
    default_image_size = inception.inception_v2.default_image_size
    def func(images):
      with slim.arg_scope(inception.inception_v2_arg_scope(
          weight_decay=weight_decay)):
        return inception.inception_v2(images,
                                      num_classes=num_classes,
                                      is_training=is_training)
    model_fn = func
  elif name == 'inception_v3':
    default_image_size = inception.inception_v3.default_image_size
    def func(images):
      with slim.arg_scope(inception.inception_v3_arg_scope(
          weight_decay=weight_decay)):
        return inception.inception_v3(images,
                                      num_classes=num_classes,
                                      is_training=is_training)
    model_fn = func
  elif name == 'lenet':
    default_image_size = lenet.lenet.default_image_size
    def func(images):
      with slim.arg_scope(lenet.lenet_arg_scope(
          weight_decay=weight_decay)):
        return lenet.lenet(images,
                           num_classes=num_classes,
                           is_training=is_training)
    model_fn = func
  elif name == 'resnet_v1_50':
    default_image_size = resnet_v1.resnet_v1.default_image_size
    def func(images):
      with slim.arg_scope(resnet_v1.resnet_arg_scope(
          is_training, weight_decay=weight_decay)):
        net, end_points = resnet_v1.resnet_v1_50(
            images, num_classes=num_classes)
        net = tf.squeeze(net, squeeze_dims=[1, 2])
        return net, end_points
    model_fn = func
  elif name == 'resnet_v1_101':
    default_image_size = resnet_v1.resnet_v1.default_image_size
    def func(images):
      with slim.arg_scope(resnet_v1.resnet_arg_scope(
          is_training, weight_decay=weight_decay)):
        net, end_points = resnet_v1.resnet_v1_101(
            images, num_classes=num_classes)
        net = tf.squeeze(net, squeeze_dims=[1, 2])
        return net, end_points
    model_fn = func
  elif name == 'resnet_v1_152':
    default_image_size = resnet_v1.resnet_v1.default_image_size
    def func(images):
      with slim.arg_scope(resnet_v1.resnet_arg_scope(
          is_training, weight_decay=weight_decay)):
        net, end_points = resnet_v1.resnet_v1_152(
            images, num_classes=num_classes)
        net = tf.squeeze(net, squeeze_dims=[1, 2])
        return net, end_points
    model_fn = func
  elif name == 'vgg_a':
    default_image_size = vgg.vgg_a.default_image_size
    def func(images):
      with slim.arg_scope(vgg.vgg_arg_scope(weight_decay)):
        return vgg.vgg_a(images,
                         num_classes=num_classes,
                         is_training=is_training)
    model_fn = func
  elif name == 'vgg_16':
    default_image_size = vgg.vgg_16.default_image_size
    def func(images):
      with slim.arg_scope(vgg.vgg_arg_scope(weight_decay)):
        return vgg.vgg_16(images,
                          num_classes=num_classes,
                          is_training=is_training)
    model_fn = func
  elif name == 'vgg_19':
    default_image_size = vgg.vgg_19.default_image_size
    def func(images):
      with slim.arg_scope(vgg.vgg_arg_scope(weight_decay)):
        return vgg.vgg_19(images,
                          num_classes=num_classes,
                          is_training=is_training)
    model_fn = func
  else:
    raise ValueError('Model name [%s] was not recognized' % name)

  model_fn.default_image_size = default_image_size

  return model_fn
