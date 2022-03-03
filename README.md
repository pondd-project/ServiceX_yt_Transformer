# ServiceX_yt_Transformer

## Install [ServiceX frontend](https://github.com/ssl-hep/ServiceX_frontend)
```
pip install servicex==2.4.4a1
```

## Python code example
```
# import servicex frontend 
from servicex import ServiceXDataset
from servicex.servicex_python_function import ServiceXPythonFunction

# user-defined function to operate on yt data
def transform_yt(ds):
    slc = ds.r[ds.domain_center[0], :, :].plot(("gas", "density"))
    sac = slc.frb[("gas", "density")].d
    return sac

if __name__ == "__main__":
    # define DID: see https://github.com/pondd-project/ServiceX_DID_Finder_Girder
    dataset = "girder://579fb0aa7b6f0800011ea3b6#item"
    
    # pass dataset to ServiceX
    ds = ServiceXDataset(dataset, 
                         backend_name = "python"
    )
    
    # encode user function 
    selection = ServiceXPythonFunction(ds)
    encoded_selection = selection._encode_function(transform_yt)
    
    # return pandas dataframe from dataset
    r = ds.get_data_pandas_df(encoded_selection)
    print(r)
```

## Configuration
Make sure you have a servicex.yaml file in your directory. This file tells ServiceX the connection information to your instance of ServiceX:

```
api_endpoints:
  - endpoint: {servicex-host}
    name: python
    type: python

# This is the path of the cache. The "/tmp" will be translated, platform appropriate, and
# the env variable USER will be replaced.
cache_path: /tmp/servicex_${USER}

# This is a dummy value, here only to make sure that unit testing
# works properly before package release.
testing_value: 10

# If we can't figure out what backend the user is going to use, we
# return this sort of file. Parquet for the uproot backend, and root for the
# xaod backend.
default_return_data: parquet

# Defaults for the various types of servicex backends that we might deal with.
# Easy enough to add a new one here...
backend_types:
  - type: python
    return_data: parquet
```
