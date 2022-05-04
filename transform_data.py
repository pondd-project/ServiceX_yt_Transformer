# Copyright (c) 2022, University of Illinois/NCSA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os
import sys
import time
import logging
import pyarrow as pa
import pyarrow.parquet as pq
import requests
import yt
import pandas
import zipfile


def transform_data(file_path, output_path):
    logging.basicConfig(filename= os.path.join(output_path, 'transform.log'),
                        level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger(file_path)
    logger.info(f"Transforming data: {file_path}")

    try:
        start_transform = time.time()
        # download data
        if not os.path.isdir('data'):
            os.makedirs('data')
        with requests.get(file_path, stream=True) as response:
            response.raise_for_status()
            zip_file = os.path.join('data','data.zip')
            with open(zip_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192): 
                    f.write(chunk)

        # unzip file
        zip_dir = zip_file.strip('.zip')
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(zip_dir)

        # load dataset
        status = []
        for folder in zip_ref.namelist():
            try:
                filepath = zip_dir + '/{zd}/'.format(zd=folder)
                ds = yt.load(filepath)
                # run user-provided transform code
                from generated_transformer import transform_yt
                selection = transform_yt(ds)
                # save selection as parquet file
                df = pandas.DataFrame(selection)
                table = pa.Table.from_pandas(df)
                pq_filename = filepath.strip('/').rsplit('/',1)[1] + '.parquet'
                pq_filepath = os.path.join(output_path,pq_filename)
                writer = pq.ParquetWriter(pq_filepath,table.schema)
                writer.write_table(table=table)
                writer.close()
                output_size = os.stat(pq_filepath).st_size
                logger.info("Wrote {} bytes after transforming {}".format(output_size, pq_filepath))
                status.append(0)
            
            except BaseException as error:
                mesg = f"Problem loading data {file_path}: {error}"
                logger.exception(mesg)
                status.append(1)
                pass  

        end_transform = time.time()
        logger.info('Ran generated_transformer.py in ' +
                    f'{round(end_transform - start_transform, 2)} sec')
   
        if 0 not in status:
            msg = f'yt failed to load data {filepath}'
            logger.exception(msg)
            raise Exception(msg)

    except Exception as error:
        mesg = f"Failed to transform input file {file_path}: {error}"
        logger.exception(mesg)

def compile_code():
    import generated_transformer
    pass

if __name__ == '__main__':
    file_path = sys.argv[1]
    output_path = sys.argv[2]
    compile_code()
    transform_data(file_path, output_path)
