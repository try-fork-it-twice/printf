import random

start = 1
state = ["start", "change", "end"]
def get(start, state, letter="", istart=1, iend=250):
    for i in range(istart, iend):
        end = random.randint(start+3, start + 10)
        second_stage = random.randint(start+1, end-2)
        third_stage = random.randint(second_stage+1, end-1)

        print()
        print(f"section Task{letter}{i}")
        print(f"{state[0]}: {start},{second_stage}")
        print(f"{state[1]}: {second_stage},{third_stage}")
        print(f"{state[2]}: crit,{third_stage},{end}")
        start = end +1

get(start, state, "A")
get(start, state, "B")
get(start, state, "C")
get(start, state, "D")
get(start, state, "A2")
get(start, state, "B2")
get(start, state, "C2")
get(start, state, "D2")
get(start, state, "A1")
get(start, state, "B1")
get(start, state, "C1")
get(start, state, "D1")