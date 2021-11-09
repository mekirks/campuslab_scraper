
#%%
from scraper import functions as fun

#%%

fun.scrape_multiples()

#%%

url = r'https://tigerlink.fhsu.edu/organizations'
uniID = r'10175'
uni_name = r'Fort Hays State University'

fun.scrape_single(url, uniID, uni_name)
# %%
