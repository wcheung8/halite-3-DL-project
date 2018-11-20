import copy
import json
import os
import os.path
import pickle
import time
from tqdm import tqdm, tqdm_notebook
from glob import glob
import numpy as np

import hlt

try:
    import zstd
except:
    pass

ARBITRARY_ID = -1


def parse_replay_file(file_name):
    print("Load Replay: " + file_name)

    with open(file_name, 'rb') as f:
        try:
            data = json.loads(f.read())
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File {file_name} not found.")  # os.listdir(os.getcwd())

    player_list = [p['name'] for p in data['players']]
    print(f"Parsing data for {player_list}")

    replay = []
    for player in tqdm_notebook(data['players']):
        replay.append(parse_player_data(data, player))
    return np.array(replay)
        


def parse_player_data(data, player):
    """
    try:
        player = [p for p in data['players'] if p['name'].split(" ")[0] == player_name][0]
    except IndexError as e:
        return
    """

    print(f"Load Basic Information for {player}")
    
    player_id = int(player['player_id'])
    my_shipyard = hlt.Shipyard(player_id, ARBITRARY_ID,
                               hlt.Position(player['factory_location']['x'], player['factory_location']['y']))
    other_shipyards = [
        hlt.Shipyard(p['player_id'], ARBITRARY_ID, hlt.Position(p['factory_location']['x'], p['factory_location']['y']))
        for p in data['players'] if int(p['player_id']) != player_id]
    width = data['production_map']['width']
    height = data['production_map']['height']

    print("Load Cell Information")
    first_cells = []
    for x in range(len(data['production_map']['grid'])):
        row = []
        for y in range(len(data['production_map']['grid'][x])):
            row += [hlt.MapCell(hlt.Position(x, y), data['production_map']['grid'][x][y]['energy'])]
        first_cells.append(row)
    frames = []
    for f in data['full_frames']:
        prev_cells = first_cells if len(frames) == 0 else frames[-1]._cells
        new_cells = copy.deepcopy(prev_cells)
        for c in f['cells']:
            new_cells[c['y']][c['x']].halite_amount = c['production']
        frames.append(hlt.GameMap(new_cells, width, height))

    print("Load Player Ships")
    moves = [{} if str(player_id) not in f['moves'] else {m['id']: m['direction'] for m in f['moves'][str(player_id)] if
                                                          m['type'] == "m"} for f in data['full_frames']]
    ships = [{} if str(player_id) not in f['entities'] else {
        int(sid): hlt.Ship(player_id, int(sid), hlt.Position(ship['x'], ship['y']), ship['energy']) for sid, ship in
        f['entities'][str(player_id)].items()} for f in data['full_frames']]

    print("Load Other Player Ships")
    other_ships = [
        {int(sid): hlt.Ship(int(pid), int(sid), hlt.Position(ship['x'], ship['y']), ship['energy']) for pid, p in
         f['entities'].items() if
         int(pid) != player_id for sid, ship in p.items()} for f in data['full_frames']]

    print("Load Droppoff Information")
    first_my_dropoffs = [my_shipyard]
    first_them_dropoffs = other_shipyards
    my_dropoffs = []
    them_dropoffs = []
    for f in data['full_frames']:
        new_my_dropoffs = copy.deepcopy(first_my_dropoffs if len(my_dropoffs) == 0 else my_dropoffs[-1])
        new_them_dropoffs = copy.deepcopy(first_them_dropoffs if len(them_dropoffs) == 0 else them_dropoffs[-1])
        for e in f['events']:
            if e['type'] == 'construct':
                if int(e['owner_id']) == player_id:
                    new_my_dropoffs.append(
                        hlt.Dropoff(player_id, ARBITRARY_ID, hlt.Position(e['location']['x'], e['location']['y'])))
                else:
                    new_them_dropoffs.append(
                        hlt.Dropoff(e['owner_id'], ARBITRARY_ID, hlt.Position(e['location']['x'], e['location']['y'])))
        my_dropoffs.append(new_my_dropoffs)
        them_dropoffs.append(new_them_dropoffs)
    return list(zip(frames, moves, ships, other_ships, my_dropoffs, them_dropoffs))


def parse_replay_folder(folder_name, max_files=None):
    dump_file = f"game-data-{time.time()}.pkl"

    replays = sorted(glob(os.path.join(folder_name,"*.hlt")) + glob(os.path.join(folder_name, "*halite*")))
    if max_files:
        replays = replays[:max_files]

    replay_buffer = []
    for file_name in tqdm_notebook(replays):
        if max_files is not None and len(replay_buffer) >= max_files:
            break
        else:
            print(f"Parsing file {len(replay_buffer)+1}")
            replay_buffer.append(parse_replay_file(file_name))
            if len(replay_buffer) % 10 == 0:
                with open(dump_file, "wb") as f:
                    pickle.dump(replay_buffer, f)
                    f.close()

    return np.array(replay_buffer)
