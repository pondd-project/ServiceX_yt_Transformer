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
