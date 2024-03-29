import math
import random
import time
import numpy

import map


class Player:
    def __init__(self, color):
        '''
        Initializes Player object

        Args:
            color (int, int, int): player's color
        '''

        self.color = color
        self.additional_dice = 0


class Gameplay:
    '''
    Gameplay object. This class containts most of game's logic, including
    enemys AI, turn system, fighthing, etc.
    '''

    def __init__(self, map_, die_sides_number, fight_time, 
                 max_dice_on_single_hex):
        '''
        Initializes Gameplay object

        Args: 
            map_ (Map): Map object

            die_sides_number (int): how many sides single die has

            fight_time (int): time of single fight in ms

            max_dice_on_single_hex (int): maximum ammount of dice 
                on a single hex
        '''

        self.map_ = map_
        self.die_sides_number = die_sides_number
        self.fight_time = fight_time
        self.max_dice_on_single_hex = max_dice_on_single_hex

        self.is_enemy_playing = False

        self.attacking_hex = None
        self.defending_hex = None

        self.fight_finished = False

        self.attacking_hex_power = 0
        self.defending_hex_power = 0

        self.current_player_index = 0

        self.ai_coords_and_hexes_list = []


    def turn(self):
        '''
        Adds dice to human player's hexes and run ai script
        '''

        self.add_dice(self.map_.players[0])
        self.current_player_index = 1
        self.prepare_enemy_ai()

    def finish_turn(self):
        '''
        Finishes turn
        '''

        self.current_player_index = 0

    def finish_single_ai_turn(self):
        '''
        Adds dice to player's hexes and increments current player
        '''

        self.attacking_hex = None
        self.defending_hex = None
        self.add_dice(self.map_.players[self.current_player_index])
        self.current_player_index += 1


    def __ai_get_hex_enemy_neighbours(self, hex_coords):
        '''
        Returns list of hex's neighbours

        Args:
            hex_coords (int, int): hex's coords given as 2d array index

        Returns:
            list(Hex): list of neighbours
        '''

        neighbours = []

        if hex_coords[0] > 0:
            neighbours.append(self.map_.hex_map[hex_coords[0] - 1,
                              hex_coords[1]])
            if hex_coords[1] < self.map_.size[1] - 1:
                neighbours.append(self.map_.hex_map[hex_coords[0] - 1,
                                  hex_coords[1] + 1])

        if hex_coords[0] < self.map_.size[0] - 1:
            neighbours.append(self.map_.hex_map[hex_coords[0] + 1,
                              hex_coords[1]])
            if hex_coords[1] > 0:
                neighbours.append(self.map_.hex_map[hex_coords[0] + 1,
                                  hex_coords[1] - 1])

        if hex_coords[1] > 0:
            neighbours.append(self.map_.hex_map[hex_coords[0],
                              hex_coords[1] - 1])

        if hex_coords[1] < self.map_.size[1] - 1:
            neighbours.append(self.map_.hex_map[hex_coords[0],
                              hex_coords[1] + 1])

        neighbours = [hex_ for hex_ in neighbours if type(hex_) == map.Hex]
        return [hex_ for hex_ in neighbours if hex_.player !=
                self.map_.players[self.current_player_index]]


    def __ai_select_best_target(self, dice_number, neighbours):
        '''
        Returns easiest targets to attack

        Args:
            dice_number (int): attacking hex dice number

            neighbours (list(Hex)): list of neighbour hexes

        Returns:
            list(Hex): list of neighbours with lowest dice number
        '''

        neighbours.sort(key=lambda x: x.dice_number)
        neighbours = [
            hex_ for hex_ in neighbours if hex_.dice_number ==
            neighbours[0].dice_number and hex_.dice_number <= dice_number]

        return neighbours


    def __ai_attack(self, neighbours):
        '''
        Randomly attacks one of the neighbours

        Arguments:
            neighbours (list(Hex)): list of neighbour hexes
        '''

        self.defending_hex = neighbours[random.randrange(len(neighbours))]
        self.fight()


    def handle_ai(self):
        '''
        Handles single enemy ai
        '''

        if self.current_player_index > 0:
            if self.ai_coords_and_hexes_list:
                self.enemy_ai(self.ai_coords_and_hexes_list[0])
                self.ai_coords_and_hexes_list.pop(0)
            else:
                self.finish_single_ai_turn()
                if self.current_player_index < len(self.map_.players):
                    self.prepare_enemy_ai()
                else:
                    self.finish_turn()      


    def prepare_enemy_ai(self):
        '''
        Creates list of all of single player hexes and their coords
        '''

        for coords, hex_ in numpy.ndenumerate(self.map_.hex_map):
            if type(hex_) == map.Hex:
                if hex_.player == self.map_.players[self.current_player_index]:
                    if hex_.dice_number > 1:
                        self.ai_coords_and_hexes_list.append((coords, hex_))                


    def enemy_ai(self, coords_and_hex):
        '''
        Selects best target and attacks it

        Args:
            coors_and_hex ((int, int), Hex): hex's coords and hex
        '''

        neighbours = self.__ai_get_hex_enemy_neighbours(coords_and_hex[0])
        neighbours = self.__ai_select_best_target(
            coords_and_hex[1].dice_number, neighbours)

        if len(neighbours) > 0:
            self.attacking_hex = coords_and_hex[1] 
            self.__ai_attack(neighbours)


    def add_dice(self, player):
        '''
        Adds dice to player's hexes

        Arguments:
            player (Player): Player object
        '''

        hex_list = [
            hex_ for hex_ in self.map_.hex_map.flat if type(hex_) == map.Hex]
        hex_list = [hex_ for hex_ in hex_list if hex_.player == player]

        # Dice is a number of connected hexes. For example you can have two 
        # groups of 10 and 5 connected hexes. Dice will be 10, because
        # it selects larger group
        dice = self.__count_connected_hexes(player)
        # dice_to_add is dice + ammount of dice that player has in stock
        dice_to_add = dice + player.additional_dice

        max_dice_on_single_hex_to_add = 0
        for hex_ in hex_list:
            max_dice_on_single_hex_to_add += (
                self.max_dice_on_single_hex - hex_.dice_number)

        # Dice on single field cannot exceed max_dice_on_single_hex
        # Leftovers are stored in player.additional_dice
        # Maximum leftover is 4 * max_dice_on_single_hex
        player.additional_dice = dice_to_add - max_dice_on_single_hex_to_add
        if player.additional_dice < 0:
            player.additional_dice = 0
        elif player.additional_dice > 4 * self.max_dice_on_single_hex:
            player.additional_dice = 4 * self.max_dice_on_single_hex

        if dice_to_add > max_dice_on_single_hex_to_add:
            dice_to_add = max_dice_on_single_hex_to_add

        for die in range(dice_to_add):
            while True:
                hex_ = hex_list[random.randrange(len(hex_list))]
                if hex_.dice_number < self.max_dice_on_single_hex:
                    hex_.dice_number += 1
                    break


    def __count_connected_hexes(self, player):
        '''
        Returns number of player's connected hexes. It returns
        bigger of any groups. So if player has 3 connected groups then
        ammount of connected hexes in the biggest one will be returned

        Args:
            player (Player): Player object

        Returns:
            (int): ammount of connected hexes
        '''

        hex_map = numpy.copy(self.map_.hex_map)
        hex_and_coords_list = []
        count_ = 0
        max_ = 0

        for coords, hex_ in numpy.ndenumerate(hex_map):
            if type(hex_) == map.Hex:
                if hex_.player == player:
                    hex_and_coords_list.append([hex_, coords])

                    for hex_in_list in hex_and_coords_list:
                        coords = hex_in_list[1]

                        for dir_ in range(6):
                            new_coords = self.__move_hex_coords(coords, dir_)
                            hex_connected = self.__get_connected_hex(
                                player, new_coords)

                            if hex_connected and \
                                [hex_connected, new_coords] not in \
                                    hex_and_coords_list:
                                hex_and_coords_list.append(
                                    [hex_connected, new_coords])
                                hex_map[
                                    self.__move_hex_coords(coords, dir_)] = 0

                    count_ = len(hex_and_coords_list)
                    if max_ < count_:
                        max_ = count_

                    hex_and_coords_list = []

        return max_


    def __move_hex_coords(self, hex_coords, direction):
        '''
        Returns hex's coords moved to given direction. 
        Direction 0 means top left side and it goes clockwise

        Args:
            hex_coords (int, int): hex's coords given as 2d array index

            direction (int): direction (0 .. 5)

        Returns:
            (int, int): hex's coord given as 2d array index moved
        '''

        hex_coords_moved = list(hex_coords)
        if direction == 0:
            if hex_coords[0] > 0:
                hex_coords_moved[0] -= 1
        elif direction == 1:
            if hex_coords[0] > 0 and hex_coords[1] < self.map_.size[1] - 1:
                hex_coords_moved[0] -= 1
                hex_coords_moved[1] += 1
        elif direction == 2:
            if hex_coords[0] < self.map_.size[0] - 1:
                hex_coords_moved[0] += 1
        elif direction == 3:
            if hex_coords[0] < self.map_.size[0] - 1 and hex_coords[1] > 0:
                hex_coords_moved[0] += 1
                hex_coords_moved[1] -= 1
        elif direction == 4:
            if hex_coords[1] > 0:
                hex_coords_moved[1] -= 1
        elif direction == 5:
            if hex_coords[1] < self.map_.size[1] - 1:
                hex_coords_moved[1] += 1

        return tuple(hex_coords_moved)


    def __get_connected_hex(self, player, hex_coords):
        '''
        Returns hex if it's owner is given player, else returns None

        Args:
            player (Player): Player object

            hex_coords (int, int): hex's coords given as 2d array index

        Returns:
            Hex or None: hex with given coords
        '''

        hex_ = self.map_.hex_map[hex_coords]

        if type(hex_) == map.Hex:
            if hex_.player == player:
                return hex_

        return None


    def fight_finish(self):
        '''
        Checks if fight is finished, does a break and prepares for the next fight
        '''

        if self.fight_finished:
            if self.fight_time > 0:
                time.sleep(self.fight_time / 1000)

            # If attacking player has won the fight conquer defending hex
            # Leaving one dice behind and move dice to conquered hex
            if self.attacking_hex_power > self.defending_hex_power:
                self.defending_hex.player = self.attacking_hex.player
                self.defending_hex.dice_number = \
                    self.attacking_hex.dice_number - 1
                self.attacking_hex.dice_number = 1
            # If player has lost the fight leave one dice on attacking field
            else:
                self.attacking_hex.dice_number = 1

            self.attacking_hex = None
            self.defending_hex = None
            self.attacking_hex_power = 0
            self.defending_hex_power = 0

            self.fight_finished = False


    def fight(self):
        '''
        Rolls dice for attacking and defending hex and finishes fight
        '''

        if self.attacking_hex and self.defending_hex:
            for die in range(self.attacking_hex.dice_number):
                self.attacking_hex_power += random.randrange(
                    1, self.die_sides_number + 1)

            for die in range(self.defending_hex.dice_number):
                self.defending_hex_power += random.randrange(
                    1, self.die_sides_number + 1)

            self.fight_finished = True


    def is_hex_next_to_attacking_hex(self, hex_):
        '''
        Returns True if attacking hex is neighbour with hex_

        Arguments:
            hex_ {Hex}: candidate hex

        Returns:
            True if attacking hex is neighbour with hex_
        '''

        max_distance_between_two_neighbour_hexes = math.sqrt(
            self.map_.half_side_length_root3 ** 2 +
            (self.map_.side_length + self.map_.half_side_length) ** 2)

        distance = math.sqrt((
            self.attacking_hex.middle[0] - hex_.middle[0]) ** 2 +
            (self.attacking_hex.middle[1] - hex_.middle[1]) ** 2)

        if distance > max_distance_between_two_neighbour_hexes:
            return False

        return True
