import json
from pprint import pprint
import csv


def remove_cdata(d: dict):
    try:
        return d["#cdata-section"]
    except TypeError:
        return d


with open("listings.json") as f:
    listings = json.load(f)

listings = listings["rss"]["channel"]["item"]

postmeta_keys = set()

output_all = []
for listing in listings:
    output_dict = dict()
    # pprint(listing)
    for field in ("title", "wp:post_modified_gmt", "link", "content:encoded"):
        output_dict[field] = remove_cdata(listing[field])

    # TODO add in category

    postmeta = listing["wp:postmeta"]
    for item in postmeta:
        if type(postmeta) is dict:
            continue
        else:

            key, value = remove_cdata(item["wp:meta_key"]), remove_cdata(
                item["wp:meta_value"]
            )
            # except TypeError as e:
            # print(postmeta)
            # print(type())
            # raise (e)
            postmeta_keys.add(key)

        if key in (
            "facebook_url",
            "twitter_url",
            "website_url",
            "address_1",
            "address_2",
            "address_3",
            "address_city",
            "address_country",
            "address_postcode",
            "eligibility_criteria",
            "hours_of_operation",
            "access_details",
            "email_address",
            "phone_number",
        ):
            if value:
                output_dict[key] = value

        elif key in ("map_location",):
            try:
                if value != "":
                    print(f"{value!r}")
                    value = json.loads(value)
                    # NB this control flow means that this needs to be the last item in the for loop
                else:
                    continue
            except Exception as e:
                pprint(listing)
                raise (e)
            output_dict["location_lat"] = float(value["center"]["lat"])
            output_dict["location_lng"] = float(value["center"]["lng"])

    output_all.append(output_dict)

with open("listings_out.json", "w") as f:
    json.dump(output_all, f)


with open("listings.csv", "w") as f:
    all_keys = set()
    for d in output_all:
        for key in d.keys():
            if not key.startswith("_oembed"):
                all_keys.add(key)
    dw = csv.DictWriter(f, all_keys)
    dw.writeheader()
    dw.writerows(output_all)


pprint(postmeta_keys)
