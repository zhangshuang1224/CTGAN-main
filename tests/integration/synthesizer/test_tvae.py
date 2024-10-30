#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Integration tests for tvae.

These tests only ensure that the software does not crash and that
the API works as expected in terms of input and output data formats,
but correctness of the data values and the internal behavior of the
model are not checked.
"""

import numpy as np
import pandas as pd

from ctgan.synthesizers.tvae import TVAE


def test_drop_last_false():
    """Test the TVAE predicts the correct values."""
    data = pd.DataFrame({'1': ['a', 'b', 'c'] * 150, '2': ['a', 'b', 'c'] * 150})

    tvae = TVAE(epochs=300)
    tvae.fit(data, ['1', '2'])

    sampled = tvae.sample(100)
    correct = 0
    for _, row in sampled.iterrows():
        if row['1'] == row['2']:
            correct += 1

    assert correct >= 95


def test__loss_function():
    """Test the TVAE produces average values similar to the training data."""
    data = pd.DataFrame({
        '1': [float(i) for i in range(1000)],
        '2': [float(2 * i) for i in range(1000)],
    })

    tvae = TVAE(epochs=300)
    tvae.fit(data)

    num_samples = 1000
    sampled = tvae.sample(num_samples)
    error = 0
    for _, row in sampled.iterrows():
        error += abs(2 * row['1'] - row['2'])

    avg_error = error / num_samples

    assert avg_error < 400


def test_fixed_random_seed():
    """Test the TVAE with a fixed seed.

    Expect that when the random seed is reset with the same seed, the same sequence
    of data will be produced. Expect that the data generated with the seed is
    different than randomly sampled data.
    """
    # Setup
    data = pd.DataFrame({
        'continuous': np.random.random(100),
        'discrete': np.random.choice(['a', 'b', 'c'], 100),
    })
    discrete_columns = ['discrete']

    tvae = TVAE(epochs=1)

    # Run
    tvae.fit(data, discrete_columns)
    sampled_random = tvae.sample(10)

    tvae.set_random_state(0)
    sampled_0_0 = tvae.sample(10)
    sampled_0_1 = tvae.sample(10)

    tvae.set_random_state(0)
    sampled_1_0 = tvae.sample(10)
    sampled_1_1 = tvae.sample(10)

    # Assert
    assert not np.array_equal(sampled_random, sampled_0_0)
    assert not np.array_equal(sampled_random, sampled_0_1)
    np.testing.assert_array_equal(sampled_0_0, sampled_1_0)
    np.testing.assert_array_equal(sampled_0_1, sampled_1_1)


def test_tvae_save(tmpdir, capsys):
    """Test that the ``TVAE`` model can be saved and loaded."""
    # Setup
    data = pd.DataFrame({
        'continuous': np.random.random(100),
        'discrete': np.random.choice(['a', 'b', 'c'], 100),
    })
    discrete_columns = ['discrete']

    tvae = TVAE(epochs=10, verbose=True)
    tvae.fit(data, discrete_columns)
    captured_out = capsys.readouterr().err
    tvae.set_random_state(0)

    tvae.sample(100)
    model_path = tmpdir / 'model.pkl'

    # Save
    tvae.save(str(model_path))

    # Load
    loaded_instance = TVAE.load(str(model_path))
    sampled = loaded_instance.sample(100)

    # Assert
    assert sampled.shape == (100, 2)
    assert isinstance(sampled, pd.DataFrame)
    assert set(sampled.columns) == set(data.columns)
    assert set(sampled.dtypes) == set(data.dtypes)
    loss_values = tvae.loss_values
    assert len(loss_values) == 10
    assert set(loss_values.columns) == {'Epoch', 'Batch', 'Loss'}
    assert all(loss_values['Batch'] == 0)
    last_loss_val = loss_values['Loss'].iloc[-1]
    assert f'Loss: {round(last_loss_val, 3):.3f}: 100%' in captured_out
