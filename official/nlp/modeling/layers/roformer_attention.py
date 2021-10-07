# Copyright 2021 The TensorFlow Authors. All Rights Reserved.
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

"""
Modified from attention.py
"""

"""Keras-based attention layer."""
# pylint: disable=g-classes-have-attributes
import math

import tensorflow as tf

EinsumDense = tf.keras.layers.experimental.EinsumDense
MultiHeadAttention = tf.keras.layers.MultiHeadAttention


def _build_trig_vector(length, key_dim):
    tf_dtype = tf.keras.mixed_precision.global_policy().compute_dtype
    position_ids = tf.cast(tf.range(length), dtype=tf_dtype)  # (length,) (0,2,...,m-1) FIXME: is position id start from 0
    position_ids = tf.expand_dims(position_ids, axis=0)  # (1, length)
    steps = key_dim // 2
    indices = tf.cast(tf.range(steps), dtype=tf_dtype)  # (key_dim/2,) (0,2,...,i-1)
    indices = tf.pow(tf.constant(10000.0, dtype=tf_dtype), -2 * indices / steps)  # (key_dim/2,) 10000^{-2(i-1)/d}
    vec = tf.einsum('bl,d->bld', position_ids, indices)  # (1, length, key_dim/2) m10000^{-2(i-1)/d}
    sin_vec = tf.repeat(tf.sin(vec), repeats=2, axis=-1)  # (1, length, key_dim) sin(m10000^{-2(i-1)/d})
    cos_vec = tf.repeat(tf.cos(vec), repeats=2, axis=-1)  # (1, length, key_dim) cos(m10000^{-2(i-1)/d})
    sin_vec, cos_vec = tf.expand_dims(sin_vec, 2), tf.expand_dims(cos_vec, 2)  # (1, length, 1, key_dim)
    return sin_vec, cos_vec


@tf.keras.utils.register_keras_serializable(package="Text")
class RoformerAttention(tf.keras.layers.MultiHeadAttention):
  def roformer_recompute_qkv(self,
                             q,
                             k,
                             v):
      q_shape = tf.shape(q)
      q_len = q_shape[1]
      k_shape = tf.shape(k)
      k_len = k_shape[1]

      q_sin_vec, q_cos_vec = _build_trig_vector(q_len, self._key_dim)
      k_sin_vec, k_cos_vec = _build_trig_vector(k_len, self._key_dim)
      q2 = tf.stack([-q[..., 1::2], q[..., ::2]], axis=4)
      q2 = tf.reshape(q2, q_shape)
      k2 = tf.stack([-k[..., 1::2], k[..., ::2]], axis=4)
      k2 = tf.reshape(k2, k_shape)
      ret_q = q * q_cos_vec + q2 * q_sin_vec
      ret_w = k * k_cos_vec + k2 * k_sin_vec
      return ret_q, ret_w, v


  def call(self,
           query,
           value,
           key=None,
           attention_mask=None,
           return_attention_scores=False,
           training=None):
    if not self._built_from_signature:
      self._build_from_signature(query=query, value=value, key=key)
    if key is None:
      key = value

    #   N = `num_attention_heads`
    #   H = `size_per_head`
    # `query` = [B, T, N ,H]
    query = self._query_dense(query)

    # `key` = [B, S, N, H]
    key = self._key_dense(key)

    # `value` = [B, S, N, H]
    value = self._value_dense(value)

    query, key, value = self.roformer_recompute_qkv(query, key, value)

    attention_output, attention_scores = self._compute_attention(
        query, key, value, attention_mask, training)
    attention_output = self._output_dense(attention_output)

    if return_attention_scores:
      return attention_output, attention_scores
    return attention_output