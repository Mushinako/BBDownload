import defconst


def fetch():
    # Get Personal Data from JSON
    with open('data/data.json', 'r') as personal_data:
        pd = json.loads
