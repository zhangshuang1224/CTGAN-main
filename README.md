
**Using `pip`:**

```bash
pip install ctgan
```

**Using `conda`:**

```bash
conda install -c pytorch -c conda-forge ctgan
```

When using the CTGAN library directly, you may need to manually preprocess your data into the correct format, for example:

* Continuous data must be represented as floats
* Discrete data must be represented as ints or strings
* The data should not contain any missing values

# Usage Example

In this example we load the [Adult Census Dataset](https://archive.ics.uci.edu/ml/datasets/adult)* which is a built-in demo dataset. We use CTGAN to learn from the real data and then generate some synthetic data.

```python3
from ctgan import CTGAN
from ctgan import load_demo

real_data = load_demo()

# Names of the columns that are discrete
discrete_columns = [
    'workclass',
    'education',
    'marital-status',
    'occupation',
    'relationship',
    'race',
    'sex',
    'native-country',
    'income'
]

ctgan = CTGAN(epochs=10)
ctgan.fit(real_data, discrete_columns)

# Create synthetic data
synthetic_data = ctgan.sample(1000)
```

