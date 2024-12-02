
import json
import os
import time
import requests

from utils.yaml_utils import read_yaml_file

REQUESTS_DELAY_S = 5

class AoCInputReader:    
    def __init__(self, session_cookie: str = None, year:int = 2024):
        self.max_requests = 10
        self.session_cookie = session_cookie    
        self.year = year
              
    
    def get_input(self, day: int):
        if os.path.exists(f"data/inputs/day{day}.txt"):
            print("Reading data from file.")
            data = self.read_input(day)
        else:
            print(f"File not found, downloading input for day {day}")
            if self.session_cookie is None:
                raise ValueError("Session cookie not found. Please provide a session cookie.")
            
            requests_made = 0            
            response_status = 0
            while response_status != 200 and requests_made < self.max_requests:
                try: 
                    print(f"Try {requests_made + 1}/{self.max_requests}")
                    response = self.fetch_aoc_input(day)
                except requests.exceptions.HTTPError as e:
                    print(f"Error fetching input: {e} \nTrying again in {REQUESTS_DELAY_S} seconds")
                    time.sleep(REQUESTS_DELAY_S)
                finally:
                    requests_made += 1
                    response_status = response.status_code
            data = [str(line) for line in response.text.splitlines(f"\n")]
            self.save_input(data, day)
        return self.read_input(day)
    
    
    def read_input(self,day: int) -> dict:
        with open(f"data/inputs/day{day}.txt", "r") as file:
            data = file.read()
            lines = data.splitlines()
            return lines 

    def save_input(self,data: dict,day: int):
        path = f"data/inputs/day{day}.txt"
        with open(path, "w") as file:
            file.writelines(data)

    def fetch_aoc_input(self,day: int):
        headers: dict[str, str] = {
            "cookie": f"session={self.session_cookie}",
            "User-Agent": "AoC Input Fetcher Script"
        }
        
        response = requests.get(f"https://adventofcode.com/{self.year}/day/{day}/input", headers=headers)
        
        if response.status_code == 200:
            return response
        else:
            raise requests.exceptions.HTTPError(f"Error fetching input: {response.status_code}, {response.reason}")
        

def read_input(day: int, year:int) -> list[str]:
    session_cookie = read_yaml_file("config.yaml")["session_cookie"]
    input_reader = AoCInputReader(session_cookie, year)
    return input_reader.get_input(day)