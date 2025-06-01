from copy import deepcopy
from sh import gunzip as sh__gunzip
from os.path import join as os__path__join
from urllib.request import urlretrieve

output_directory = "data_input"
list_url = [
    "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.5.0.2.0/analysis/diagnostics/" +
        "HadCRUT.5.0.2.0.analysis.summary_series.global.monthly.nc",
    "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.5.0.2.0/analysis/diagnostics/" +
        "HadCRUT.5.0.2.0.analysis.component_series.global.monthly.nc",
    " https://www.metoffice.gov.uk/hadobs/hadisst/data/HadISST_sst.nc.gz",
    "https://downloads.psl.noaa.gov/Datasets/gpcp/precip.mon.mean.nc"
]
for k in list_url:
    u = deepcopy(k)
    f = os__path__join(output_directory, k.split("/")[-1])
    urlretrieve(u, f)
    if f[-3:] == ".gz":
        sh__gunzip(f)

# if you have a certificate error see:
# https://stackoverflow.com/questions/68275857/urllib-error-urlerror-urlopen-error-ssl-certificate-verify-failed-certifica
