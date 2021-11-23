
#%%
from scraper import functions as fun

#%%

fun.scrape_multiples()

#%%

url = r'https://ttu.campuslabs.com/engage/organizations'
uniID = r'10175'
uni_name = r'Texas Tech University'

fun.scrape_single(url, uniID, uni_name)
# %%
