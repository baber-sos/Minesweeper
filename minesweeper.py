user_board = [[0,0,0,0,0,1,1,1,0],
        [0,0,1,1,1,1,-1,1,0],
        [0,0,1,-1,2,2,2,1,0],
        [1,1,3,2,3,-1,1,0,0],
        [2,-1,4,-1,3,2,1,0,0],
        [2,-1,-1,3,-1,1,0,0,0],
        [1,2,2,2,1,1,0,0,0],
        [0,0,1,1,1,0,1,1,1],
        [0,0,1,-1,1,0,1,-1,1]]

def check_if_finished(board, game_size):
    for i in range(game_size[0]):
        for j in range(game_size[1]):
            if board[i][j] == -2:
                return False;

    return True;


##generates the possible mine locations
def gen_neighbors(coord, game_size, open_cells):
    ret_list = [];
    mine_count = user_board[coord[0]][coord[1]];
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            temp = (coord[0] + i, coord[1] + j);
            if (i != 0 or j != 0) and temp[0] >= 0 and temp[0] < game_size[0] and\
                    temp[1] >= 0 and temp[1] < game_size[1]:
                if temp in open_cells:
                    if open_cells[temp][0] == -1:
                        mine_count -= 1;
                    continue;

                ret_list.append(temp);
    return (mine_count, [(mine_count, set(ret_list))]);

##remove neighbors which may be considered a potential mine right now
##second argument is a set of clear cells to remove
def remove_cells(open_cells, to_remove, mine_case):
    cell_mine_list = [];
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            temp = (to_remove[0] + i, to_remove[1] + j);
            if temp in open_cells and (i != 0 or j != 0):
                cell_mine_list.append(temp);
    #print(cell_mine_list);
    for neighbor in cell_mine_list:
        total_mines, possible_mines = open_cells[neighbor];
        #print ('this is the cell I am removing from\n', neighbor, possible_mines);
        new_possible_mines = [];
        for number, mine in possible_mines:
            if to_remove in mine:
                total_mines -= mine_case;
                new_possible_mines.append((number - mine_case, mine - set([to_remove])));
            else:
                new_possible_mines.append((number, mine));
        #print(neighbor, total_mines, new_possible_mines);        
        open_cells[neighbor] = (total_mines, new_possible_mines);
    return open_cells;

##adds cells to open cells which are sure to be clear
def add_cells(open_cells, unknowns, game_size, board):
    #print(unknowns);
    #something does nothing more than unpack things
    for something in unknowns:
        for cell in something[1]:
            if cell not in open_cells:
                open_cells[cell] = gen_neighbors(cell, game_size, open_cells);
                #print('this is the cell: ', cell);
                open_cells = remove_cells(open_cells, cell, 0);
                board[cell[0]][cell[1]] = user_board[cell[0]][cell[1]];
    return open_cells;


def count_unknown_neighbors(unknowns):
    #print('this is the mine count: ', unknowns);
    to_ret = 0;
    for _, mine_set in unknowns[1]:
        to_ret += len(mine_set);
    return to_ret;

def calculate_probabilities(open_cells, cells):
    min_probability = float('inf');
    min_set = set();
    for prob_cell in cells:
        for num, mine_set in open_cells[prob_cell][1]:
            if num == 0:
                return (0, mine_set);
            cur_prob = float(num)/len(mine_set);
            if cur_prob < min_probability:
                min_probability = cur_prob;
                min_set = mine_set;
    return (min_probability, min_set);

#this function will check if it can extract some useful information using the information avalable
#for cells which have intersection with the given one.
def intersect_and_divide(open_cells, cell):
    intersecting_cells = [];
    for i in [-2, -1, 0, 1, 2]:
        for j in [-2, -1, 0, 1, 2]:
            if i == 0 and j == 0:
                continue;
            temp = (cell[0] + i, cell[1] + j);
            if temp in open_cells and open_cells[temp][0] not in [-2, 0, -1]:
                #print(temp, temp[0]
                intersecting_cells.append(temp);
    #print(intersecting_cells);
    #input('printing the intersections!');
    update_flag = False;
    for inter_cell in intersecting_cells:
        #print('original cell unknowns: ', cell, open_cells[cell]);
        cell_uk = open_cells[cell];
        temp_track = {};
        for number, mine_set in cell_uk[1]:
            #print('intersecting cells uk: ', inter_cell, open_cells[inter_cell]);
            inter_uk = open_cells[inter_cell];
            #if inter_cell == (3, 3):
                #print(cell_uk, inter_uk);
            flag = False;
            for inum, imine_set in inter_uk[1]:
                left = (mine_set, cell, number) if number < inum else (imine_set, inter_cell, inum);
                right =  (mine_set, cell, number) if number >= inum else (imine_set, inter_cell, inum);
                inter = left[0] & right[0]; uni_left = set(); uni_right = set();
                if inter != set():
                    uni_left = left[0] - right[0]; uni_right = right[0] - left[0];
                else:
                    temp_track.setdefault(inter_cell, []).append((inum, imine_set));
                    continue;

                if uni_left == set():
                    #if inter_cell == (3, 3):
                        #print('I was here!!', left[1], right[1])
                    update_flag = True if uni_right != set() else False;
                    if right[1] == cell:
                        flag = True;
                    new_right = [(left[2], left[0]), (right[2] - left[2], uni_right)];
              
                    if uni_right == set():
                        new_right.pop();
                    temp_track.setdefault(right[1], []); 
                    temp_track[right[1]] = temp_track[right[1]] + new_right;
                    temp_track.setdefault(left[1], []).append((left[2], left[0]));
                    #update_flag = True;
                    break;
                else:
                    count_valid = 0;
                    valid_arrange = ();
                    for i in range(0, min(len(uni_left), left[2]) + 1):
                        inter_count = left[2] - i;
                        if inter_count > len(inter):
                            continue;
                        if right[2] - inter_count > len(uni_right):
                            continue;
                        count_valid += 1;
                        if count_valid > 1:
                            break;
                        valid_arrange = (i, inter_count, right[2] - inter_count);

                    if count_valid == 1:
                        update_flag = True;
                        #print('count valid triggered!', (valid_arrange[1], inter, left[1]));
                        temp_track.setdefault(left[1], []) 
                        temp_track[left[1]] = temp_track[left[1]] + [(valid_arrange[0], uni_left),
                                (valid_arrange[1], inter)];
                        temp_track.setdefault(right[1], []) 
                        temp_track[right[1]] = temp_track[right[1]] + [(valid_arrange[1], inter),
                                (valid_arrange[2], uni_right)];
                        flag = True;
                    else:
                        temp_track.setdefault(inter_cell, []).append((inum, imine_set));
            if not flag:
                temp_track.setdefault(cell, []).append((number, mine_set));
            #if inter_cell == (3, 3):
                #print('temp', temp_track);
            open_cells[inter_cell] = (open_cells[inter_cell][0], temp_track[inter_cell]);
            temp_track[inter_cell] = [];
        open_cells[cell] = (open_cells[cell][0], temp_track[cell]);
        temp_track[cell] = [];
    
    return open_cells, calculate_probabilities(open_cells, [cell] + intersecting_cells), update_flag;

def playgame(game_size):
    board = [[-2 for i in range(game_size[1])] for j in range(game_size[0])];
    done = False;
    ##these are the non-zero cells which have been opened and still have 
    ##unknown neighbors left
    open_cells = {};
    open_cells[(0,0)] = gen_neighbors((0, 0), game_size, open_cells); #(user_board[0][0],\
            #[(user_board[0][0], gen_neighbors((0,0), game_size, open_cells))]);
    #print(user_board[0][0], gen_neighbors((0,0), game_size, open_cells));
    board[0][0] = user_board[0][0];
    while not done:
        update_flag = False;
        min_probability = (float('inf'), set());
        for cell in list(open_cells.keys()):
            unknowns = open_cells[cell];
            print(cell, unknowns);
            ##this handles the zero case and is working pretty well
            if unknowns[0] in [-2, -1]:
                continue;
            clear_indices = [];
            for i in range(len(unknowns[1])):
                if unknowns[1][i][0] == 0:
                    #if division_flag and cell == (3, 3):
                    #    print(cell, unknowns, open_cells[cell], clear_indices);
                    add_cells(open_cells, [unknowns[1][i]], game_size, board);
                    #if division_flag and cell == (3, 3):
                    #    print(cell, unknowns, open_cells[cell], clear_indices);
                    clear_indices.append(i);
                    update_flag = True;
                elif unknowns[1][i][0] == len(unknowns[1][i][1]):
                    clear_indices.append(i);
                    update_flag = True;
                    for mine_cell in unknowns[1][i][1]:
                        remove_cells(open_cells, mine_cell, 1);
                        open_cells[mine_cell] = (-1, []);
                        board[mine_cell[0]][mine_cell[1]] = -1;
            
            #if division_flag and cell == (3, 3):
            #    print(cell, unknowns, open_cells[cell], clear_indices);

            if clear_indices == []:
                #print('divide and conquer');
                #print(unknowns);
                #if cell == (3,2) and len(unknowns[1][0][1]) == 3:
                    #print('before division');
                    #for k, v in open_cells.items():
                    #    print(k, v);
                open_cells, cur_min_probability, cur_flag = intersect_and_divide(open_cells, cell);
                print('this the current flag: ', cur_flag);
                if cur_flag == True:
                    update_flag = True;
                if cur_min_probability[0] < min_probability[0]:
                    min_probability = cur_min_probability;
                    #print('after first divsion: ');
                    #for k, v in open_cells.items():
                    #    print(k, v);
                    #print('------');
                    #input('first division ended here');
                division_flag = True;
            count = 0;
            for ind in clear_indices:
                #print('index', ind, unknowns);
                del unknowns[1][ind - count];
                count += 1;
            if unknowns[1] == []:
                open_cells[cell] = (-2, [])

            #elif unknowns[0] == 0:
            #    add_cells(open_cells, unknowns[1], game_size, board);
            #    open_cells[cell] = (-2, []);
            #    continue;
            #elif unknowns[0] == count_unknown_neighbors(unknowns):
            #    for _, mine_coords in unknowns[1]:
            #        for mine_cell in mine_coords:
            #            remove_cells(open_cells, mine_cell, 1);
            #            open_cells[mine_cell] = (-1, []);
            #            board[mine_cell[0]][mine_cell[1]] = -1;
            #    print('something found'); 
            #else:##only intersections are remaining!
            #   continue
           ##rest of the game solver logic
           ##we have to handle two simple cases and one probabilistic and logical case
            #continue;
        if update_flag == False:
            print('this is the minimum probability: ', min_probability);
        for i in range(len(board)):
            print(board[i]);
        input('press enter to continue playing!');
    return;
if __name__ == '__main__':
    playgame((9,9));
