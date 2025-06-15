import requests

baseUrl = "https://catboy.best"
ppCalcEndpoint = "/api/calc/pp/{}?mods=72"

def main():
    # Ask for user input
    beatmap_id = input("Enter a beatmap ID: ").strip()

    # Construct full URL
    url = baseUrl + ppCalcEndpoint.format(beatmap_id)
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad status codes
        data = response.json()
        print("Response from server:")
        print(data)
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Connection Error:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong:", err)
    except ValueError:
        print("Failed to parse JSON from response.")

if __name__ == "__main__":
    main()
