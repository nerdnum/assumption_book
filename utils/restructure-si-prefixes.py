import csv
import json

# name	symbol	factor	name

with open("utils/si-prefixes.txt", "r") as f:
    csv_reader = csv.reader(f, delimiter="\t")
    si_prefixes = []
    count = 1
    for line in csv_reader:
        exponent = int(line[2])
        if exponent > 15:
            category = "extra-largest"
            available = False
        if exponent in [12, 15]:
            category = "largest"
            available = True
        if exponent in [3, 6, 9]:
            category = "larger"
            available = True
        if exponent in [1, 2]:
            category = "large"
            available = True
        if exponent < -15:
            category = "extra-smallest"
            available = False
        if exponent in [-12, -15]:
            category = "smallest"
            available = True
        if exponent in [-3, -6, -9]:
            category = "smaller"
            available = True
        if exponent in [-1, -22]:
            category = "small"
            available = True

        si_prefixes.append(
            {
                "id": count,
                "text": line[0],
                "symbol": line[1],
                "factor": "10^{}".format(line[2]),
                "name": line[3],
                "category": category,
                "available": available,
            }
        )
        count += 1
    with open("utils/si-prefixes.json", "w") as f:
        f.write(json.dumps(si_prefixes, indent=2))
        print("File si-prefixes.json created successfully")

# largest
# larger
# large
# medium
# small
# smaller
# smallest
