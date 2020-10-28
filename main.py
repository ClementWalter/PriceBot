import re

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

#%% Get page
urls = [
    "https://www.kingpower.com/dior/category/womens-fragrance?lang=en",
    "https://www.kingpower.com/dior/category/mens-fragrance?lang=en",
    "https://www.kingpower.com/dior/category/makeup?lang=en",
    "https://www.kingpower.com/dior/category/skincare?lang=en",
]
data = []
for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features="html5lib")
    products = soup.find_all("div", re.compile(".*ProductDesc.*"))

    for product in products:
        data += [
            (
                pd.DataFrame(
                    [
                        {
                            "class_name": content.attrs["class"][0],
                            "content": np.array(
                                content.contents, dtype="object"
                            ).flatten()[0]
                            if content.contents
                            else None,
                        }
                        for content in product.contents
                    ]
                )
                .assign(
                    description=lambda df: df.class_name.str.extract(
                        r".*__(?P<description>\w+)-sc", expand=False
                    )
                )
                .loc[lambda df: df.description.str.contains(r"Name|Price")]
                .set_index("description")
                .content
            )
        ]

pd.DataFrame(data).to_csv("kingpower.csv", index=False)
